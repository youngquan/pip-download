import logging
import sys
from collections import OrderedDict

from cachecontrol import CacheControl
from pip._internal.index import PackageFinder
from pip._vendor.packaging.specifiers import SpecifierSet
from pip._internal.download import PipSession

import click
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

sess = requests.Session()
session = CacheControl(sess)


def get_pypi_url(package_name: str, package_version: str=None) -> str:
    url_prefix = 'https://pypi.python.org/pypi/'
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
            if dependencies is not None:
                for dependency in dependencies:
                    if ';' not in dependency:
                        if ' ' in dependency:
                            package_name, package_version_bracket = dependency.split(' ')
                            package_version = package_version_bracket[1:-1]
                            finder = PackageFinder(find_links=list(), index_urls=['https://pypi.org/simple'],
                                                   session=PipSession())
                            candidates = finder.find_candidates(package_name, SpecifierSet(specifiers=package_version))
                            package_version = str(candidates.get_best().version)
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
              type=click.File(),
              help='Requirements File.')
def pipdownload(packages: str, requirement_file):
    for package in packages:
        if '==' in package:
            package_name, package_version = package.split('==')
        else:
            package_name = package
            package_version = None
        requirements_dep = OrderedDict()
        requirements = OrderedDict()
        requirements_dep[package_name] = PythonPackage(package_name, package_version, package, None)
        while requirements_dep:
            package = requirements_dep.popitem(last=False)
            dependencies = get_dependencies(package[1], requirements)
            if dependencies is not None:
                    requirements_dep.update(dependencies)

        for package_name, package_info in requirements.items():
            logger.info('Downloading %s...' % package_info.show_name)


if __name__ == '__main__':
    pipdownload()

