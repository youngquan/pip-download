pip-download
============

pip-download is a tool which can be used to download python projects and their dependencies listed on
pypi's `download files` page. If you run the `pip-download` command to download one project on a Linux platform,
packages end with `.whl` and can be directly installed on a Windows and a macOS platform will also be downloaded.
In that way, you can use these downloaded packages to serve for a minimal
pypi sever(like `pypiserver <https://pypi.org/project/pypiserver/>`_ on your company internal network.

At first, it uses `pip download xxx` command to download packages of the project `xxx` to a temp dir. Then it unpacks
these downloaded packages' name and version to download all packages of the project `xxx`. These downloaded
packages include packages end with `.whl` built on the Linux, Windows, macOS platform and the source packages end with
`.tar.gz` or `.zip` .

.. contents:: **Table of Contents**
    :backlinks: none

Installation
------------

pip-download is distributed on `PyPI <https://pypi.org>`_ and is available on Linux/macOS and Windows and supports
Python 3.5+. You can simply install pip-download as below:

.. code-block:: bash

    $ pip install pip-download

However, it's a better choice to use a virtual environment:

.. code-block:: bash

    $ python -m venv venv
    # On Windows:
    $ .\venv\Scripts\activate
    # On Linux:
    $ .venv/bin/activate
    $ pip install pip-download

`virtualenv <https://virtualenv.pypa.io/en/latest/>`_ is also a good choice.

Usage
-----

After installation, you can use pip-download to download python projects and its dependencies.

.. code-block:: bash
    
    $ pip-download flask
    $ pip-download -r requirements.txt
    $ pip-download hatch -d /tmp/

License
-------

pip-download is distributed under the terms of both

- `MIT License <https://choosealicense.com/licenses/mit>`_
- `Apache License, Version 2.0 <https://choosealicense.com/licenses/apache-2.0>`_

at your option.

Credits
-------

- All the people who work on `Click <https://github.com/pallets/click>`_
- All the people involved in the project `hatch <https://github.com/ofek/hatch>`_
