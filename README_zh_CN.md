# pip-download - 一个跨平台跨 Python 版本的 Python 包下载工具

因为我在一个离线的环境下从事 Python 开发工作，受限于导入资料的昂贵成本，我经常需要不断下载导入 Python 包及其依赖到我的工作环境中去，也常常面临着以下的情况：

- 手头只有 windows 的上网环境，但是我想下载 linux 操作系统上的 Python 包。

- 电脑上安装了 Python3.6，但是我想下载 Python 2 或者 Python 3.8 版本等其它 Python 版本的  Python 包。
- 我想一次性尽量多地下载不同 Python 版本不同操作系统的 Python Wheel 包和 Python 源码包，因为害怕遗漏了某个版本某个操作系统的 Python 包及其依赖，而不得不重新导入。
- 我在离线的环境里搭建了一个本地的 pypi 源，我希望下载不同平台、不同 Python 版本的 wheel 包和源码包一次性导入，满足离线环境里跨平台跨 Python 版本的开发需求。

官方的 Python 包管理器 pip 直接提供了 [download](https://pip.pypa.io/en/stable/reference/pip_download/) 子命令，还提供了`--platform`, `--python-version`, `--implementation`, `--abi` 等选项，但总是很难适应上面的场景。这些参数不仅内容繁重，拥有诸多的限制，遇到下载的某个依赖包没有指定格式的时候，常常会中断下载。举个例子，当你在装有 Python 3.7 的 windows 上执行如下命令时，便会遇到中断下载的情况：

```powershell
> pip download --only-binary=:all: --platform manylinux1_x86_64 --python-version 36 --implementation cp --abi cp36m  tensorflow==1.14.0
...
ERROR: Could not find a version that satisfies the requirement wrapt>=1.11.1 (from tensorflow==1.14.0) (from versions: none)
ERROR: No matching distribution found for wrapt>=1.11.1 (from tensorflow==1.14.0)
...
```

可以看到，tensorflow 依赖 wrapt 这个包，因为指定了必须下载 Wheel 包，而 wrapt 没有提供相应的 Wheel 包，因而出现了上面的问题。总的来说，在下载 Python 包这方面 pip 真的不是一个好工具，多用几次你就会有切身的体会了。

正是基于上面的原因，我开发了 pip-download 这个 Python 库，可以一键下载一个 Python 工程及其依赖，包含了这个 Python 项目上传到 pypi 上的所有文件（在 `Download files` 页面展现）。

## 小试牛刀

```bash
$ pip install pip-download -U
...

$ pip-download flask
...
All packages have been downloaded successfully!
```

## 安装方法

pip-download 支持 Python 3.6 + ，可直接通过 pip 进行安装：

```bash
$ pip install pip-download
```

更加推荐在 Python 虚拟环境中安装：

```bash
$ python -m venv venv
$ source venv/bin/activate
$ pip install pip-download
```

## 使用说明

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
  --show-config               When specified, the config file and config
                              content will be shown.
  --help                      Show this message and exit.

```

