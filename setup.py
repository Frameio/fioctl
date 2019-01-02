#!/usr/bin/env python3

from setuptools import setup

with open("README.md", "r") as f:
  long_description = f.read()

setup(name='fioctl',
      version='1.0',
      description='Frame.io cli',
      long_description=long_description,
      packages=['fioctl'],
      include_package_data=True,
      install_requires=[
        'Click==6.7',
        'pyyaml',
        'requests',
        'tqdm',
        'frameioclient==0.5.1',
        'tabulate',
        'token-bucket',
        'treelib',
        'cached-property',
        'furl'
      ],
      entry_points={
        'console_scripts': 'fioctl=fioctl.fioctl:cli'
      },
      author='Frame.io, Inc.',
      author_email='platform@frame.io',
      license='MIT')