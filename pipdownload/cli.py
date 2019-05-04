import logging
import os
import sys
from collections import OrderedDict
import itertools

from cachecontrol import CacheControl
from pip._internal.index import PackageFinder
from pip._internal.utils.temp_dir import TempDirectory
from pip._vendor.packaging.specifiers import SpecifierSet
from pip._internal.download import PipSession, unpack_url
from pip._vendor.packaging.requirements import Requirement, InvalidRequirement
from pip._internal.commands.download import DownloadCommand

import click
import requests

from tqdm import tqdm
import math

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

sess = requests.Session()
session = CacheControl(sess)

options, args = DownloadCommand().parse_args(['requests=1.2.1'])
# dis_dir = options['src_dir']
dis_dir = os.getcwd()

build_delete = True



def get_pypi_url(package_name: str, package_version: str=None) -> str:
    url_prefix = 'https://pypi.python.org/pypi/'
    finder = PackageFinder(find_links=list(), index_urls=['https://pypi.org/simple'],
                           session=PipSession())
    candidates = finder.find_candidates(package_name, SpecifierSet(specifiers=package_version))
    package_version = str(candidates.get_best().version)
    if package_version:
        url = url_prefix + '{0}/{1}/json'.format(package_name, package_version)
    else:
        url = url_prefix + '{0}/json'.format(package_name)
    return url


class PythonPackage:
    def __init__(self, name, version, show_name, download_urls):
        self.name = name
        self.version = version
        self.show_name = show_name if show_name else '{0}({1})'.format(name, version)
        self.download_urls = download_urls

    def __str__(self):
        return self.show_name


def get_dependencies(package: PythonPackage, requirements: OrderedDict):
    url = get_pypi_url(package.name, package.version)
    try:
        r = session.get(url)
        if r.status_code == 200:
            package_data = r.json()
            dependencies = package_data['info']['requires_dist']
            package.download_urls = package_data['urls']
            requirements.update({package.name: package})
            dependency_packages = OrderedDict()
            if dependencies:
                for dependency in dependencies:
                    if ';' not in dependency:
                        if ' ' in dependency:
                            package_name, package_version_bracket = dependency.split(' ')
                            package_version = package_version_bracket[1:-1]
                        else:
                            package_name = dependency
                            package_version = None
                        dependency_package = PythonPackage(package_name,
                                                           package_version,
                                                           package.show_name + ' -> ' + dependency,
                                                           None)
                        dependency_packages.update({package_name: dependency_package})
                result = dependency_packages
            else:
                result = None
            logger.info('Package %s has be processed!' % package.show_name)
            return result

    except ConnectionError as e:
        logger.error('Can not access JSON information about package %s, and the Exception is below.', package)
        logger.error(e)
        raise





@click.command()
@click.argument('packages', nargs=-1)
@click.option('-r', '--requirement', 'requirement_file',
              type=click.File(encoding='utf-8'),
              help='Requirements File.')
def pipdownload(packages: str, requirement_file):
    # for package in requirement_file:
    #     print(package)
    if requirement_file:
        packages_extra = {req.strip() for req in requirement_file}
    else:
        packages_extra = set()
    for package in itertools.chain(packages_extra, packages):
        try:
            req = Requirement(package)
        except InvalidRequirement:
            logging.error('Invalid requirement: %s' % package)
        package_name = req.name
        package_version = str(req.specifier)
        requirements_dep = OrderedDict()
        requirements = OrderedDict()
        requirements_dep[package_name] = PythonPackage(package_name, package_version, package, None)
        while requirements_dep:
            package = requirements_dep.popitem(last=False)
            dependencies = get_dependencies(package[1], requirements)
            if dependencies is not None:
                    requirements_dep.update(dependencies)

        with TempDirectory(
                options.build_dir, delete=build_delete, kind="download"
        ) as directory:
            for _, package_info in requirements.items():
                for download_url in package_info.download_urls:

                    unpack_url(download_url['url'], directory, dis_dir, only_download=True,
                               session=PipSession(), progress_bar="on")
                    logger.info('Downloading %s...' % package_info.show_name)




url = "http://example.com/bigfile.bin"
# Streaming, so we can iterate over the response.
r = requests.get(url, stream=True)

# Total size in bytes.
total_size = int(r.headers.get('content-length', 0))
block_size = 1024
wrote = 0
with open('output.bin', 'wb') as f:
    for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size//block_size), unit='KB', unit_scale=True):
        wrote = wrote + len(data)
        f.write(data)
if total_size != 0 and wrote != total_size:
    print("ERROR, something went wrong")
if __name__ == '__main__':
    pipdownload()

