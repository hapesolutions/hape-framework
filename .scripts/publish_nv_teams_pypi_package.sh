#!/bin/bash
set -e
# make sure to call this script from the make file only
PACKAGE_DIRECTORY="./publish/nv-connectors"
PYPI_REPOSITORY_URL="https://mynexus/repository/nv-pypi/"

mkdir -p $PACKAGE_DIRECTORY
rm -rf $PACKAGE_DIRECTORY/*

cp ./src/connectors/*.py $PACKAGE_DIRECTORY/

touch $PACKAGE_DIRECTORY/__init__.py

echo """
# Title
This is the Readme File
# Getting Started
These are the steps
""" > $PACKAGE_DIRECTORY/README.md

echo """
from setuptools import setup

setup(
    name='nv-connectors',
    version='0.1',
    description='Connector to 3rd-party development and communication tools',
    author='Hazem Ataya',
    author_email='hazem.ataya94@gmail.com',
    packages=['nv-connectors'],
    install_requires=[
        'requests>=2.31.0',
    ],
)
""" > $PACKAGE_DIRECTORY/setup.py

# build package
cd $PACKAGE_DIRECTORY/..
rm -rf dist/*
python setup.py sdist bdist_wheel

# upload
# pip install twine
# twine upload --repository-url $PYPI_REPOSITORY_URL dist/*
cd -
