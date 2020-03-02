#!/usr/bin/python
from setuptools import find_packages,setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="deepevent",
    version="0.2",
    author="Lempereur Mathieu",
    author_email="mathieu.lempereur@univ-brest.fr",
    description="Deep Learning to identify gait events",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LempereurMat/deepevent/archive/v0.2.tar.gz",
    include_package_data=True,
    packages=find_packages(),
    scripts=['deepevent/deepevent.py'],
    install_requires=['tensorflow','keras','numpy','scipy','pyBTK'],
    classifiers=['Programming Language :: Python',
                 'Programming Language :: Python :: 3.7',
                 'Operating System :: Microsoft :: Windows',
                 'Natural Language :: English'],

)
