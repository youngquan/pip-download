# pip-download: A wrapper useful in offline scenario

[简体中文]( https://github.com/youngquan/pip-download/blob/master/README_zh_CN.md)

pip-download is a tool which can be used to download python projects and their dependencies listed on
pypi's `download files` page. If you run the `pip-download` command to download one project on a Linux platform, packages end with `.whl` and can be directly installed on a Windows and a macOS platform will also be downloaded. In that way, you can use these downloaded packages to serve for a minimal pypi sever(like [pypiserver](https://pypi.org/project/pypiserver/) ) on your company internal network.

At first, it uses `pip download xxx` command to download packages of the project `xxx` to a temp dir. Then it unpacks these downloaded packages' name and version to download all packages of the project `xxx`. These downloaded packages include packages end with `.whl` built on the Linux, Windows, macOS platform and the source packages end with `.tar.gz` or `.zip` .

## Installation

pip-download is distributed on [PyPI]( https://pypi.org ) and is available on Linux/macOS and Windows and supports
Python 3.6+. You can simply install pip-download as below:

```bash
$ pip install pip-download
```

However, it's a better choice to use a virtual environment:

```bash
$ python -m venv venv
# On Windows:
$ .\venv\Scripts\activate
# On Linux:
$ source venv/bin/activate
$ pip install pip-download
```

[virtualenv](https://virtualenv.pypa.io/en/latest/) is also a good choice.

## Usage

After installation, you can use pip-download to download python projects and its dependencies.

```bash
$ pip-download flask
$ pip-download -r requirements.txt
$ pip-download hatch -d /tmp/
$ pip-dwonload -py cp37 ujson
$ pip-dwonload -py cp37 -p win_amd64 ujson
```

Also, you can put your common options in the config file, `python_versions` and `platform_tags` are supported now:

```bash
$ pip-download --show-config
/some-path-to/settings.json

$ vim /some-path-to/settings.json
{
    "python-versions": ["cp37"],
    "platform-tags": ["win_amd64"]
}

$ vim /some-path-to/settings.json
{
    "python-versions": ["cp37", "cp36"],
    "platform-tags": ["win_amd64", "manylinux"]
}
```

For more usage, use `pip-download --help`.

## Credits

- All the people who work on [Click](https://github.com/pallets/click)
- All the people involved in the project [hatch](<https://github.com/ofek/hatch>)
