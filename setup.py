#!/usr/bin/env python
from setuptools import setup, find_packages

VERSION = '1.3.9'

setup(
    name='gtwpy',
    version=VERSION,
    author='prior',
    author_email='mprior@hubspot.com',
    packages=find_packages(),
    url='https://github.com/HubSpot/gtwpy',
    download_url='https://github.com/HubSpot/gtwpy/tarball/v%s'%VERSION,
    license='LICENSE.txt',
    description='A kickass wrapper around the Citrix GoToWebinar REST API',
    long_description=open('README.rst').read(),
    install_requires=[
        'sanetime>=4,<5',
        'utilspy>=0,<1',
        'giftwrap>=1,<2',
        'gevent<2',
    ],
    dependency_links=[
        'https://bitbucket.org/denis/gevent/get/82f623ff862a.tar.gz#egg=gevent'   # gevent 1.0b2
    ],
    platforms=['any']
)

