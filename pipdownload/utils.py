import hashlib
import io
import logging
import os.path
import posixpath
import re
import shutil
import tempfile
import urllib
from functools import partial
from typing import BinaryIO, Dict, Generator, Iterator, List, NoReturn
from urllib.parse import urljoin, urlparse, urlunparse

import click
import requests
from packaging.utils import canonicalize_name
from pipdownload.exceptions import HashMismatch
from retrying import retry

logger = logging.getLogger(__name__)


# Retry every half second for up to 3 seconds
@retry(stop_max_delay=3000, wait_fixed=500)
def rmtree(directory: str, ignore_errors: bool = False) -> None:
    shutil.rmtree(directory, ignore_errors=ignore_errors)


class TempDirectory:
    """Helper class that owns and cleans up a temporary directory.

    This class can be used as a context manager or as an OO representation of a
    temporary directory.

    Attributes:
        path
            Location to the created temporary directory or None
        delete
            Whether the directory should be deleted when exiting
            (when used as a contextmanager)

    Methods:
        create()
            Creates a temporary directory and stores its path in the path
            attribute.
        cleanup()
            Deletes the temporary directory and sets path attribute to None

    When used as a context manager, a temporary directory is created on
    entering the context and, if the delete attribute is True, on exiting the
    context the created directory is deleted.
    """

    def __init__(self, path=None, delete=None):

        if path is None and delete is None:
            # If we were not given an explicit directory, and we were not given
            # an explicit delete option, then we'll default to deleting.
            delete = True

        self.path = path
        self.delete = delete

    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.path)

    def __enter__(self):
        self.create()
        return self

    def __exit__(self, exc, value, tb):
        if self.delete:
            self.cleanup()

    def create(self):
        """Create a temporary directory and store its path in self.path
        """
        if self.path is not None:
            logger.debug(
                "Skipped creation of temporary directory: {}".format(self.path)
            )
            return
        # We realpath here because some systems have their default tmpdir
        # symlinked to another directory.  This tends to confuse build
        # scripts, so we canonicalize the path by traversing potential
        # symlinks here.
        self.path = os.path.realpath(tempfile.mkdtemp(prefix="pipdownload-"))
        logger.debug("Created temporary directory: {}".format(self.path))

    def cleanup(self):
        """
        Remove the temporary directory created and reset state
        """
        if self.path is not None and os.path.exists(self.path):
            rmtree(self.path)
        self.path = None


class PythonPackage:
    def __init__(self, name, version):
        if name is None:
            self.name = name
        else:
            self.name = canonicalize_name(name)
        self.version = version

    def __repr__(self):
        return "{}<{!r}, {!r}>".format(self.__class__.__name__, self.name, self.version)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def read_chunks(file, size=io.DEFAULT_BUFFER_SIZE):
    """Yield pieces of data from a file-like object until EOF."""
    while True:
        chunk = file.read(size)
        if not chunk:
            break
        yield chunk


class Hashes:
    """A wrapper that builds multiple hashes at once and checks them against
    known-good values

    """

    def __init__(self, hashes: Dict[str, List[str]] = None) -> None:
        """
        :param hashes: A dict of algorithm names pointing to lists of allowed
            hex digests
        """
        self._allowed = {} if hashes is None else hashes

    def check_against_chunks(self, chunks: Iterator[bytes]) -> None:
        """
        Check good hashes against ones built from iterable of chunks of
        data.

        Raise HashMismatch if none match.

        """
        gots = {}
        for hash_name in self._allowed:
            try:
                gots[hash_name] = hashlib.new(hash_name)
            except (ValueError, TypeError):
                raise

        for chunk in chunks:
            for hash in gots.values():
                hash.update(chunk)

        for hash_name, got in gots.items():
            if got.hexdigest() in self._allowed[hash_name]:
                return
        self._raise(gots)

    def _raise(self, gots) -> NoReturn:
        raise HashMismatch({}, gots)

    def check_against_file(self, file: BinaryIO) -> None:
        """Check good hashes against a file-like object

        Raise HashMismatch if none match.

        """
        return self.check_against_chunks(read_chunks(file))

    def check_against_path(self, path: str) -> None:
        with open(path, "rb") as file:
            return self.check_against_file(file)

    def __nonzero__(self) -> bool:
        """Return whether I know any known-good hashes."""
        return bool(self._allowed)

    def __bool__(self) -> bool:
        return self.__nonzero__()


def resolve_package_file(name: str) -> PythonPackage:
    """
    Resolve the package's name and version from the full name of python package
    :param name: The name of python package
    :return: An instance of `PythonPackage`
    """
    # result is used to match the version string in the full name of python package
    result = None
    if name.endswith(".tar.gz"):
        result = re.search(r"(?<=-)[^-]+?(?=\.tar\.gz)", name)

    if name.endswith(".tar.bz2"):
        result = re.search(r"(?<=-)[^-]+?(?=\.tar\.bz2)", name)

    if name.endswith(".zip"):
        result = re.search(r"(?<=-)[^-]+?(?=\.zip)", name)

    if name.endswith(".whl"):

        result = re.search(r"(?<=-)[^-]+?(?=-p|-c)", name)
    if result is not None:
        return PythonPackage(name[: result.start() - 1], result.group(0))
    else:
        return PythonPackage(None, None)


def resolve_package_files(names: List[str]) -> Generator[PythonPackage, None, None]:
    for name in names:
        result = resolve_package_file(name)
        if result.name is not None:
            yield result


def make_absolute(link, base_url):
    parsed = urlparse(link)._asdict()
    # If link is relative, then join it with base_url.
    if not parsed["netloc"]:
        return urljoin(base_url, link)

    # Link is absolute; if it lacks a scheme, add one from base_url.
    if not parsed["scheme"]:
        parsed["scheme"] = urlparse(base_url).scheme

        # Reconstruct the URL to incorporate the new scheme.
        parsed = (v for v in parsed.values())
        return urlunparse(parsed)
    return link


def get_file_links(html_doc, base_url, python_package_local: PythonPackage) -> set:
    def gen():
        # use version to match hyperlinks in web pages, so the number of matches will get smaller.
        version = re.escape(python_package_local.version)
        for link in re.finditer(
            rf'<a.*?href="(.+?)".*?>(.+{version}.+?)</a>', html_doc
        ):
            link_href, link_text = link.groups()
            try:
                href = link_href.strip()
                python_package_on_page = resolve_package_file(link_text)
                if python_package_local == python_package_on_page:
                    if href:
                        yield make_absolute(href, base_url)
            except KeyError:
                pass

    return set(gen())


def download(url, dest_dir, quiet=False):
    file_url, file_hash = url.split("#")
    file_name = os.path.basename(file_url)
    hash_algo, hash_value = file_hash.split("=")
    hashes = Hashes({hash_algo: hash_value})
    download_file_path = os.path.join(dest_dir, file_name)
    if os.path.exists(download_file_path):
        try:
            hashes.check_against_path(download_file_path)
            logger.info("The file %s has already been downloaded." % download_file_path)
            return
        except HashMismatch:
            logger.warning(
                "Previously-downloaded file %s has bad hash. " "Re-downloading.",
                download_file_path,
            )
            os.unlink(download_file_path)

    try:
        response = requests.get(file_url, stream=True)
        chunk_size = 1024
        size = 0
        if response.status_code == 200:
            content_size = int(response.headers["content-length"])
            logger.info("Downloading file %s: " % file_name)
            with open(download_file_path, "wb") as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    if not quiet:
                        size += len(data)
                        click.echo(
                            "\r"
                            + "[Processing]:%s%.2f%%"
                            % (
                                ">" * int(size * 50 / content_size),
                                float(size / content_size * 100),
                            ),
                            nl=False,
                        )
                if not quiet:
                    click.echo("\n", nl=False)
        else:
            logger.error(
                f"The status code is {response.status_code}, and the text is {response.text}."
            )
    except ConnectionError as e:
        logger.error("Cannot download file from url: %s" % file_url)
        logger.error(e)


quiet_download = partial(download, quiet=True)


def mkurl_pypi_url(url, project_name):
    loc = posixpath.join(url, urllib.parse.quote(canonicalize_name(project_name)))
    # For maximum compatibility with easy_install, ensure the path
    # ends in a trailing slash.  Although this isn't in the spec
    # (and PyPI can handle it without the slash) some other index
    # implementations might break if they relied on easy_install's
    # behavior.
    if not loc.endswith("/"):
        loc = loc + "/"
    return loc
