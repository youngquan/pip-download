import itertools
import os
import subprocess
import sys

import click
import requests
from cachecontrol import CacheControl

from pipdownload.utils import TempDirectory, resolve_package_files, get_file_links, download, mkurl_pypi_url

from pipdownload import logger

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
                              writable=True, resolve_path=True))
def pipdownload(packages, index_url, requirement_file, dest_dir):
    # for package in requirement_file:
    #     print(package)
    if not dest_dir:
        dest_dir = os.getcwd()
    if requirement_file:
        packages_extra = {req.strip() for req in requirement_file}
    else:
        packages_extra = set()
    for package in itertools.chain(packages_extra, packages):
        with TempDirectory(delete=True) as directory:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'download', '-i', index_url,
                                       '--dest', directory.path,
                                       '--no-binary', ':all:',
                                       package])
            except subprocess.CalledProcessError as e:
                logger.warning('Can not download the package %s with no binary' % package)
                subprocess.check_call([sys.executable, '-m', 'pip', 'download', '-i', index_url,
                                       '--dest', directory.path, package])
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


if __name__ == '__main__':
    pipdownload()
