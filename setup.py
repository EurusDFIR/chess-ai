# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("src/ai/order_moves_cython.pyx")
)