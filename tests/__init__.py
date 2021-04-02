import sys
from functools import partial

if sys.version_info[1] >= 8:
    from shutil import copytree as copy

    copytree = partial(copy, dirs_exist_ok=True)
else:
    from distutils.dir_util import copy_tree as copytree  # noqa
