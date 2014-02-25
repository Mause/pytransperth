from os import walk, chdir
from os.path import join, dirname, splitext, abspath, relpath
import sys
import unittest

MODULE_DIR = join(dirname(__file__), '..')
MODULE_DIR = abspath(MODULE_DIR)


def walker(opath='.'):
    for path, folders, files in walk(opath):
        for filename in files:
            if filename.startswith('test_') and filename.endswith('.py'):
                rpath = relpath(path, opath)

                yield (rpath + '.' + splitext(filename)[0]).strip('.')


def suite():
    sys.path.insert(0, MODULE_DIR)
    sys.path.insert(0, dirname(__file__))

    SUB_UNITS = dirname(__file__)
    SUB_UNITS = walker(SUB_UNITS)

    chdir(dirname(__file__))

    return unittest.TestLoader().loadTestsFromNames(SUB_UNITS)
