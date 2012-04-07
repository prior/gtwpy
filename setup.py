#!/usr/bin/env python
from distutils.core import setup

setup(
    name='gtwpy',
    version='1.0.2',
    description='Python GoToWebinar (GTW) REST API Wrapper',
    author='Michael Prior',
    author_email='prior@cracklabs.com',
    url='https://github.com/prior/pygtw',
    download_url='https://github.com/prior/gtwpy/tarball/v1.0.2',
    packages=['gtw'],
    install_requires=[ 'nose==1.1.2' ]
)
