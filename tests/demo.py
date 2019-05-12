import urllib,  os
from tqdm import tqdm

import urllib.request

class TqdmUpTo(tqdm):
    """Provides `update_to(n)` which uses `tqdm.update(delta_n)`."""
    def update_to(self, b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)  # will also set self.n = b * bsize

eg_link = "https://pypi.tuna.tsinghua.edu.cn/packages/6e/49/43b514bfdaf4af12e6ef1f17aa25447157bcbb864c07775dacd72e8c8e02/Flask-0.1.tar.gz#sha256=9da884457e910bf0847d396cb4b778ad9f3c3d17db1c5997cb861937bd284237"
with TqdmUpTo(unit='B', unit_scale=True, miniters=1,
              desc=eg_link.split('/')[-1]) as t:  # all optional kwargs
    urllib.request.urlretrieve(eg_link, filename=os.path.join(os.getcwd(), 'demo.zip'),
                       reporthook=t.update_to, data=None)