# pip-download: 一个跨平台跨Python版本的 Python 包下载工具

如果你在离线环境下从事 Python 开发工作，你会经常需要不断下载导入 Python 包及其依赖到你的工作环境中去。如果直接使用 `pip download` 进行下载，则只会下载执行该命令时对应平台对应 Python 版本上的 whl 包。举个例子，当你在装有 Python 3.7 的 windows 上执行：

```po
> pip download MarkupSafe
...
Successfully downloaded MarkupSafe
...

> ls -Name
MarkupSafe-1.1.1-cp37-cp37m-win_amd64.whl
```

可以看到，只下载了包含 `cp37-cp37m-win_amd64` 的 wheel 包。如果你在离线的环境里搭建了一个本地的 pypi 源，你会希望下载不同平台、不同 Python 版本的 wheel 包一次性导入，减少导入次数，提升效率，同时满足离线环境里跨平台跨 Python 版本的开发体验。

正是基于上面的原因，我开发了 pip-download 这个 Python 库，可以一键下载一个 Python 工程及其依赖上传到 pypi 上的所有 wheel 包和源码。下面进行详细介绍。

# 小试牛刀

```bash
$ pip install pip-download -U
...

$ pip-download flask
```

# 安装方法

pip-download 支持 Python 3.6 + ，可直接通过 pip 进行安装：

```bash
$ pip install pip-download
```

也可以在 Python 虚拟环境中安装：

```bash
$ python -m venv env
$ source env/bin/activate
$ pip install pip-download
```

# 使用方法

pip-download 有详细的帮助文档，可以直接查看：

```bash
$ pip-download --help
Usage: pip-download [OPTIONS] [PACKAGES]...

  pip-download is a tool which can be used to download python projects and
  their dependencies listed on pypi's `download files` page. It can be used
  to download Python packages across system platforms and Python versions.

Options:
  -i, --index-url TEXT        Pypi index.
  -r, --requirement PATH      Requirements File.
  -d, --dest DIRECTORY        Destination directory.
  -p, --platform-tag TEXT     Suffix of whl packages except 'none-any', like
                              'win_amd64', 'manylinux1_x86_64', 'linux_i386'
                              and so on. It can be specified multiple times.
                              This is an option to replace option 'suffix'.
                              Default: 'win_amd64' and 'manylinux1_x86_64'.
  -py, --python-version TEXT  Version of python to be downloaded. More
                              specifically, this is the abi tag of the Python
                              package. It can be specified multiple times.
                              Like: 'cp37', 'cp36', 'cp35' and so on.
  -q, --quiet                 When specified, logs and progress bar will not
                              be shown.
  --no-source                 When specified, the source package of the
                              project that provides wheel package will not be
                              downloaded.
  --help                      Show this message and exit.
```

