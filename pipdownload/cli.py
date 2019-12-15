import itertools
import logging
import os
import shutil
import subprocess
import sys

import click
import pip_api
import requests
from cachecontrol import CacheControl
from tzlocal import get_localzone

from pipdownload import logger
from pipdownload.utils import TempDirectory
from pipdownload.utils import download as normal_download
from pipdownload.utils import (get_file_links, mkurl_pypi_url, quiet_download,
                               resolve_package_files)

sess = requests.Session()
session = CacheControl(sess)


@click.command()
@click.argument('packages', nargs=-1)
@click.option('-i', '--index-url', 'index_url',
              default='https://pypi.org/simple',
              type=click.STRING,
              help='Pypi index.')
@click.option('-r', '--requirement', 'requirement_file',
              type=click.Path(exists=True, file_okay=True,
                              resolve_path=True),
              help='Requirements File.')
@click.option('-d', '--dest', 'dest_dir',
              type=click.Path(exists=True, file_okay=False,
                              writable=True, resolve_path=True),
              help='Destination directory.')
@click.option('-s', '--suffix', 'whl_suffixes',
              type=click.STRING,
              default=['win_amd64', 'manylinux1_x86_64'],
              multiple=True,
              help='Suffix of whl packages except `none-any` `tar.gz` `zip`.')
@click.option('-py', '--python-version', 'python_versions',
              type=click.STRING,
              multiple=True,
              help='Versions of python to be downloaded! Like: cp37 cp36 and ect.')
@click.option('-q', '--quiet',
              is_flag=True,
              help='When specified, logs and progress bar will not be shown!')
def pipdownload(packages, index_url, requirement_file, dest_dir, whl_suffixes, python_versions, quiet):
    """
    pip-download is a tool which can be used to download python projects and their dependencies listed on
    pypi's `download files` page.
    """
    tz = get_localzone()
    if tz.zone in ['Asia/Shanghai', 'Asia/Chongqing']:
        index_url = 'https://pypi.tuna.tsinghua.edu.cn/simple'

    if quiet:
        logger.setLevel(logging.ERROR)
        download = quiet_download
    else:
        download = normal_download

    if not dest_dir:
        dest_dir = os.getcwd()
    # dest_dir = os.path.abspath(dest_dir)
    if requirement_file:
        packages_extra_dict = pip_api.parse_requirements(requirement_file)
        packages_extra = {str(value) for value in packages_extra_dict.values()}
    else:
        packages_extra = set()
    for package in itertools.chain(packages_extra, packages):
        with TempDirectory(delete=True) as directory:
            logger.info('We are using pip download command to download package %s' % package)
            logger.info('-' * 50)

            try:
                command = [sys.executable, '-m', 'pip', 'download', '-i', index_url,
                           '--dest', directory.path, package]
                if quiet:
                    command.extend(['--progress-bar', 'off', '-qqq'])
                subprocess.check_call(command)
            except subprocess.CalledProcessError as e:
                logger.error('Sorry, we can not use pip download to download the package %s,'
                             ' and Exception is below' % package)
                logger.error(e)
                raise
            file_names = os.listdir(directory.path)

            # if not exact:
            #     logger.info('-' * 50)
            #     logger.info('At First, we copy these files to %s' % dest_dir)
            #     for file_name in file_names:
            #         shutil.copy(os.path.join(directory.path, file_name), dest_dir)
            #     logger.info('All file have been copied!')

            for python_package in resolve_package_files(file_names):
                url = mkurl_pypi_url(index_url, python_package.name)
                try:
                    r = session.get(url)
                    for file in get_file_links(r.text, index_url, python_package):

                        if 'tar.gz' in file:
                            download(file, dest_dir)
                            continue
                        if 'none-any' in file:
                            download(file, dest_dir)
                            continue
                        if 'zip' in file:
                            download(file, dest_dir)
                            continue

                        eligible = True
                        if whl_suffixes:
                            for suffix in whl_suffixes:
                                if suffix in file:
                                    eligible = True
                                    break
                                else:
                                    eligible = False
                        if not eligible:
                            continue

                        if python_versions:
                            for version in python_versions:
                                if version in file:
                                    eligible = True
                                    break
                                else:
                                    eligible = False

                        if eligible:
                            download(file, dest_dir)

                except ConnectionError as e:
                    logger.error('Can not get information about package %s, and the Exception is below.',
                                 python_package.name)
                    logger.error(e)
                    raise
            logger.info('All packages have been downloaded successfully!')


if __name__ == '__main__':
    pipdownload()
