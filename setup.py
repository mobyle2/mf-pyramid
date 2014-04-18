#!/usr/bin/env python

from setuptools import setup, find_packages

requires = [
    'pymongo',
    'pyramid',
    'pyramid_debugtoolbar',
    'mongokit >= 0.8.2'
    ]

setup(name='mf',
      version='0.1.37',
      description='MongoKit forms generation and Pyramid Administration Dashboard',
      author='Olivier Sallou',
      author_email='olivier.sallou@irisa.fr',
      license='LGPL',
      url='https://github.com/mobyle2/mf-pyramid',
      packages=['mf'],
      install_requires=requires
     )
