import os
from pathlib import Path

from setuptools import find_packages, setup


def read(fname):
    return (Path(os.path.dirname(__file__)) / fname).read_text()


NAME = "h5tree"
DESCRIPTION = "tree for HDF5 files"
URL = "https://github.com/johnaparker/h5tree"
EMAIL = "japarker@uchicago.edu"
AUTHOR = "John Parker"
KEYWORDS = "hdf5 tree"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = "1.0"
LICENSE = "MIT"

REQUIRED = [
    "h5py",
    "termcolor",
]

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    keywords=KEYWORDS,
    entry_points={"console_scripts": ["h5tree=h5tree:main"]},
    url=URL,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    install_requires=REQUIRED,
    python_requires=REQUIRES_PYTHON,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
)
