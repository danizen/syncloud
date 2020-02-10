#!/usr/bin/env python
import os
import shutil
from distutils.command import clean

from setuptools import find_packages, setup


def get_version():
    """
    Determine a version string using a file VERSION.txt
    """
    version = '0.0.1'
    if os.path.isfile('VERSION.txt'):
        with open('VERSION.txt', 'r') as f:
            version = f.read().strip()
    return version


def get_readme():
    """
    Open and read the readme. This would be the place to convert to RST, but we no longer have to.
    """
    with open('README.md') as f:
        return f.read()


class PurgeCommand(clean.clean):
    """
    Custom command to purge everything
    """
    description = "purge 'build', 'dist', and '*.egg-info' directories"

    def run(self):
        super().run()
        if not self.dry_run:
            for path in ['build', 'dist', 'rds_secrets.egg-info']:
                os.path.isdir(path) and shutil.rmtree(path)


setup(
    name='syncloud',
    version=get_version(),
    description='Continuously push to or pull from an S3 bucket',
    long_description=get_readme(),
    long_description_content_type='text/markdown; charset=UTF-8; variant=CommonMark',
    author='Dan Davis',
    author_email='dan@danizen.net',
    url='https://github.com/danizen/syncloud/',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['boto3', 'watchdog'],
    tests_require=['virtualenv', 'tox'],
    cmdclass={
        'purge': PurgeCommand,
    },
    entry_points={
        'console_scripts': [
            'syncloud = rds_secrets.pgbouncer.script:main',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: Public Domain',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: System :: System Administration',
        'Topic :: Utilities',
    ],
)
