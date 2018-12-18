#!/usr/bin/env python3

from setuptools import setup

setup(name='fioctl',
      version='1.0',
      description='Frame.io operational tools',
      author='Michael Guarino',
      author_email='mguarino@frame.io',
      packages=['fioctl'],
      include_package_data=True,
      install_requires=[
        'Click==6.7',
        'pyyaml',
        'frameioclient==0.5.1',
        'tabulate',
        'token-bucket',
        'treelib',
        'cached-property',
        'furl'
      ],
      entry_points={
        'console_scripts': 'fioctl=fioctl.fioctl:cli'
      })