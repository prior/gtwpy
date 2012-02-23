#!/usr/bin/env python
from distutils.core import setup

setup(
    name='gtwpy',
    version='0.1',
    description='Python GoToWebinar (GTW) REST API Wrapper',
    author='Michael Prior',
    author_email='prior@cracklabs.com',
    url='https://github.com/prior/pygtw',
    download_url='https://github.com/prior/gtwpy/tarball/v0.1',
    packages=['gtw'],
    install_requires=[
        'nose==1.1.2',
        'unittest2==0.5.1',
        'sanetime==3.1.2'],
    dependency_links = ['https://github.com/prior/sanetime/tarball/v3.1.2'],
)
