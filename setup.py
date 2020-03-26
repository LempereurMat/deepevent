#!/usr/bin/python
from setuptools import find_packages,setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="deepevent",
    version="0.3.3",
    author="Lempereur Mathieu",
    author_email="mathieu.lempereur@univ-brest.fr",
    description="Deep Learning to identify gait events",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    packages=find_packages(),
    scripts=['deepevent/deepevent_script.py'],
    install_requires=['tensorflow>=2.0.0,<2.1.0',
                      'keras>=2.3.1',
                      'numpy>=1.18.1',
                      'scipy>=1.4.1',
                      'pyBTK>=0.1.1'],
    classifiers=['Programming Language :: Python',
                 'Programming Language :: Python :: 3.7',
                 'Operating System :: Microsoft :: Windows',
                 'Natural Language :: English'],

)
