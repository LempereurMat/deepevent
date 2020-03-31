#!/usr/bin/python
# -*- coding: utf8 -*-

from setuptools import find_packages,setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="deepevent",
    version="0.4",
    author="Lempereur Mathieu",
    author_email="mathieu.lempereur@univ-brest.fr",
    description="Deep Learning to identify gait events",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
	package_data={'deepevent': ['data/DeepEvent*.*']},
	#scripts=['deepevent\deepevent.py'],
    entry_points={'console_scripts': ['deepevent = deepevent.deepevent:main']},
    install_requires=['tensorflow>=2.1.0',
                      'keras>=2.3.1',
                      'numpy>=1.18.1',
                      'scipy>=1.4.1',
                      'pyBTK>=0.1.1',
					  'googledrivedownloader==0.4'],
    classifiers=['Programming Language :: Python',
                 'Programming Language :: Python :: 3.7',
                 'Operating System :: Microsoft :: Windows',
                 'Natural Language :: English'],

)
