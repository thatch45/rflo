#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Import python libs
import os
import sys

if 'USE_SETUPTOOLS' in os.environ or 'setuptools' in sys.modules:
    from setuptools import setup
else:
    from distutils.core import setup

NAME = 'rflo'
DESC = ('raft on raet and ioflo')
VERSION = '0.0.1'

setup(name=NAME,
      version=VERSION,
      description=DESC,
      author='Thomas S Hatch',
      author_email='thatch@saltstack.com',
      url='https://github.com/thatch45/rflo',
      packages=[
          'rflo',
          ]
      )
