pipdownload
===========

-----

pipdownload is a tool which can be used to download python pakcages and its dependencies listed on pypi's download files
page, like this:

  `https://pypi.org/project/<project_name>/#files` 

It use pypi's `JSON API <https://warehouse.readthedocs.io/api-reference/json/>`_ to fetch packages information about
dependecies and urls. Meanwhile, it use pip's interal method to get the best package version from package's version
specifiers.

.. contents:: **Table of Contents**
    :backlinks: none

Installation
------------

pipdownload is distributed on `PyPI <https://pypi.org>`_ and is available on Linux/macOS and Windows and supports
Python 3.5+.

.. code-block:: bash

    $ pip install pipdownload
    
Usage
-----

After installation, you can use pipdownload to download packages and its dependencies.

.. code-block:: bash
    
    $ pip download flask
    $ pip download -r requirements.txt

License
-------

pipdownload is distributed under the terms of both

- `MIT License <https://choosealicense.com/licenses/mit>`_
- `Apache License, Version 2.0 <https://choosealicense.com/licenses/apache-2.0>`_

at your option.

Credits
-------

