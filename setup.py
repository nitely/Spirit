#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
REQUIREMENTS = open(os.path.join(os.path.dirname(__file__), 'requirements.txt')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-spirit',
    version='0.1.3',
    description='Spirit is a Python based forum powered by Django.',
    author='Esteban Castro Borsani',
    author_email='ecastroborsani@gmail.com',
    long_description=README,
    url='http://spirit-project.com/',
    packages=find_packages(exclude=['example', ]),
    test_suite="run_tests.run_tests",
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
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
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
