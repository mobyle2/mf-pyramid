#!/usr/bin/env python

from setuptools import setup, find_packages

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'mf'
    ]

setup(name='mfpyramid',
      version='0.1.0',
      description='MongoKit forms generation and Pyramid Administration Dashboard',
      author='Olivier Sallou',
      author_email='olivier.sallou@irisa.fr',
      license='LGPL',
      url='https://github.com/mobyle2/mf-pyramid',
      packages=['mfpyramid'],
      install_requires=requires
     )
