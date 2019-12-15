Release History
===============

0.0.8 (2019-12-15)
------------------

- Create packages directory if it is missing

Closes #9

0.0.7 (2019-12-15)
------------------

- Do not copy files from the results from command `pip download`
- add an option `--quiet` or `-q` to display progress bars and logs
- use  pypi.org as the default pypi index, and use timezone to determine the time zone
- use package pip-api to parse the requirement file
- add three dependencies: pip-api, pip and tzlocal

Closes #1 #4 #5 #7 #8

0.0.4 (2019-05-29)
------------------

- Add option whl_suffixes to download specified whls
- Remove beautifulsoup(bs4) from requirement

0.0.3 (2019-05-22)
------------------

-   Do not try to download source tar.gz at first
-   Copy files from the temp directory to avoid download again

0.0.2 (2019-05-19)
------------------

-   Birth!

0.0.1 (2019-05-14)
------------------

-   The first release.

