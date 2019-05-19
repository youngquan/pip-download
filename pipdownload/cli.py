import itertools
import os
import subprocess
import sys

import click
import requests
from cachecontrol import CacheControl

from pipdownload import logger
from pipdownload.utils import (TempDirectory, download, get_file_links,
                               mkurl_pypi_url, resolve_package_files)

sess = requests.Session()
session = CacheControl(sess)


@click.command()
@click.argument('packages', nargs=-1)
@click.option('-i', '--index-url', 'index_url',
              default='https://pypi.tuna.tsinghua.edu.cn/simple',
              type=click.STRING,
              help='Pypi index.')
@click.option('-r', '--requirement', 'requirement_file',
              type=click.File(encoding='utf-8'),
              help='Requirements File.')
@click.option('-d', '--dest', 'dest_dir',
              type=click.Path(exists=True, file_okay=False,
                              writable=True, resolve_path=True),
              help='Destination directory.')
def pipdownload(packages, index_url, requirement_file, dest_dir):
    """
    pip-download is a tool which can be used to download python projects and their dependencies listed on
    pypi's `download files` page.
    """
    if not dest_dir:
        dest_dir = os.getcwd()
    if requirement_file:
        packages_extra = {req.strip() for req in requirement_file}
        packages_extra.remove('')
    else:
        packages_extra = set()
    for package in itertools.chain(packages_extra, packages):
        with TempDirectory(delete=True) as directory:
            logger.info('We are using pip download command to download package %s' % package)
            logger.info('-' * 50)
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'download', '-i', index_url,
                                       '--dest', directory.path,
                                       '--no-binary', ':all:',
                                       package])
            except subprocess.CalledProcessError as e:
                logger.warning("Can not download the package %s with no binary. However, it is ok."
                               "We will try to download it with binary." % package)
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'download', '-i', index_url,
                                           '--dest', directory.path, package])
                except subprocess.CalledProcessError as e:
                    logger.error('Sorry, we can not use pip download to download the package %s,'
                                 ' and Exception is below' % package)
                    logger.error(e)

            logger.info('-' * 50)
            for python_package in resolve_package_files(os.listdir(directory.path)):
                url = mkurl_pypi_url(index_url, python_package.name)
                try:
                    r = session.get(url)
                    for file in get_file_links(r.text, index_url, python_package):
                        download(file, dest_dir)

                except ConnectionError as e:
                    logger.error('Can not get information about package %s, and the Exception is below.',
                                 python_package.name)
                    logger.error(e)
                    raise
            logger.info('All packages have been downloaded successfully!')


if __name__ == '__main__':
    pipdownload()
