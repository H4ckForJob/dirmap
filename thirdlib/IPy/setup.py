#!/usr/bin/env python

# Release process:
#
#  - set version in IPy.py
#  - set version in setup.py
#  - run unit test: make
#  - run unit test: make PYTHON=python3
#  - set release date in ChangeLog
#  - git commit -a
#  - git tag -a IPy-x.y -m "tag IPy x.y"
#  - git push
#  - git push --tags
#  - python setup.py register sdist upload
#  - update the website
#
# After the release:
#  - set version to n+1 (IPy.py and setup.py)
#  - add a new empty section in the changelog for version n+1
#  - git commit -a
#  - git push

from __future__ import with_statement
import sys
from distutils.core import setup

VERSION = '0.83'

options = {}

with open('README') as fp:
    README = fp.read().strip() + "\n\n"

ChangeLog = (
    "What's new\n"
    "==========\n"
    "\n")
with open('ChangeLog') as fp:
    ChangeLog += fp.read().strip()

LONG_DESCRIPTION = README + ChangeLog
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Environment :: Plugins',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Communications',
    'Topic :: Internet',
    'Topic :: System :: Networking',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
]
URL = "https://github.com/autocracy/python-ipy"

setup(
    name="IPy",
    version=VERSION,
    description="Class and tools for handling of IPv4 and IPv6 addresses and networks",
    long_description=LONG_DESCRIPTION,
    author="Maximillian Dornseif",
    maintainer="Jeff Ferland",
    maintainer_email="jeff AT storyinmemo.com",
    license="BSD License",
    keywords="ipv4 ipv6 netmask",
    url=URL,
    download_url=URL,
    classifiers= CLASSIFIERS,
    py_modules=["IPy"],
    **options
)

