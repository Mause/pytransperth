from __future__ import print_function
from setuptools import setup
import io
import os

import transperth

here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        if not os.path.exists(filename):
            continue

        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read(
    'README.md'
    # , 'CHANGES.txt'
)


config = {
    'name': 'transperth',
    'version': transperth.__version__,
    'url': 'http://github.com/Mause/transperth/',
    'license': 'MIT',
    'author': 'Dominic May',
    'author_email': 'me@mause.me',
    # description='Automated REST APIs for existing database-driven systems',
    'long_description': long_description,
    'packages': ['transperth', 'transperth.jp', 'transperth.smart_rider'],
    'include_package_data': True,
    'package_data': {
        'transperth': ['assets/*']
    },
    'platforms': 'any',
    'test_suite': 'tests.suite',
    'classifiers': [
        'Programming Language :: Python',
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        # 'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
}

setup(**config)
