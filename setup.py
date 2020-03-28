'''
setup.py file for SWIG color_patches
'''

from distutils.core import setup, Extension
import numpy as np

color_patches_module = Extension(
    '_color_patches',
    sources=['color_patches_wrap.c', 'union_find.c', 'join_grid.c'],
)

setup(
    name = 'ColorPatches',
    version = '0.1',
    author = 'samtenka',
    ext_modules = [color_patches_module],
    py_modules = ['color_patches'],
    include_dirs = [np.get_include(),'.']
)
