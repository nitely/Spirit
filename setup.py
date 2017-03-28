#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from setuptools import setup, find_packages


BASE_DIR = os.path.join(os.path.dirname(__file__))

with open(os.path.join(BASE_DIR, 'README.md')) as f:
    README = f.read()

VERSION = __import__('spirit').__version__

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


with open(os.path.join(BASE_DIR, 'requirements.txt')) as f:
    requirements = []
    dependencies = []

    for req in f.readlines():
        req = req.strip()

        if not req:
            continue

        if req.startswith(('git+', 'http://', 'https://')):
            # Add 'git+http://...#egg=package-version'
            # to dependencies and 'package==version'
            # to requirements
            _git, egg = req.split('#egg=')
            package, version = egg.rsplit('-', 1)
            requirements.append('%s==%s' % (package, version))
            dependencies.append(req)
        else:
            requirements.append(req)


setup(
    name='django-spirit',
    version=VERSION,
    description='Spirit is a Python based forum powered by Django.',
    author='Esteban Castro Borsani',
    author_email='ecastroborsani@gmail.com',
    long_description=README,
    url='http://spirit-project.com/',
    packages=find_packages(),
    test_suite="runtests.start",
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    dependency_links=dependencies,
    license='MIT License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
