#!/usr/bin/env python

from distutils.core import setup

setup(name='mf',
      version='0.1.8',
      description='MongoKit forms generation and Pyramid Administration Dashboard',
      author='Olivier Sallou',
      author_email='olivier.sallou@irisa.fr',
      license='LGPL',
      url='https://github.com/mobyle2/mf-pyramid',
      packages=['mf'],
      install_requires=["mongokit >= 0.8.2"]
     )
