#!/usr/bin/env python
from os import path
import re
from setuptools import setup, find_packages

REGEX = '^([\w\-\.]+)[\s]*([=<>\!]+)[\s]*([0-9\.]+)+(,[<>\!=]+[0-9\.]+)*'


def required_packages_list(file_name, exclude_version=False):
    parent = path.abspath('.')
    if not file_name:
        raise RuntimeError('Pass the requirements.txt from where requires '
                           'list will be generated')
    full_path = path.join(parent, file_name)
    print("Requirements file %s" % full_path)
    pattern = re.compile(REGEX)
    requires_list = []
    contents = None
    with open(full_path) as f:
        contents = f.read()

    for line in contents.splitlines():
        match = pattern.match(line)
        if match:
            if exclude_version:
                requires_list.append(match.group(1))
            else:
                requires_list.append(match.group())

    print('Requires List %r' % requires_list)
    return requires_list


setup(
    name='timingsclient',
    description='Python client for the NPM based timings API (see https://github.com/godaddy/timings)',
    url='https://github.com/godaddy/timings-client-py',
    author='GoDaddy Operating Company, LLC',
    author_email='mverkerk@godaddy.com',
    license='MIT',
    version='1.0.0',
    install_requires=required_packages_list('requirements.txt'),
    packages=find_packages(
        exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']))
