from io import open

from setuptools import find_packages, setup

with open('pipdownload/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

REQUIRES = [
    'click',
    'requests',
    'cachecontrol',
    'packaging',
    'retrying',
    'pip-api',
    'tzlocal',
    'pip',
    'appdirs'
]

setup(
    name='pip-download',
    version=version,
    description='A wrapper for pip download in offline scenario.',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='youngquan',
    author_email='youngquan@qq.com',
    maintainer='youngquan',
    maintainer_email='youngquan@qq.com',
    url='https://github.com/youngquan/pip-download',
    license='MIT/Apache-2.0',

    keywords=[
        'pip download',
        'cross platform',
        'offline packages',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
    ],

    install_requires=REQUIRES,
    tests_require=['coverage', 'pytest', 'pytest-datadir', 'beautifulsoup4'],
    extras_require={
            'dev': [
                'isort',
                'autoflake',
                'black'
            ]
        },

    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pip-download = pipdownload.cli:pipdownload',
        ],
    },
)
