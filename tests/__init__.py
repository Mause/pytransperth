from os import walk, chdir
from os.path import join, dirname, splitext, abspath, relpath
import sys
import unittest

HERE = dirname(__file__)
MODULE_DIR = join(HERE, '..')
MODULE_DIR = abspath(MODULE_DIR)

is_test = lambda filename: (
    filename.startswith('test_') and
    filename.endswith('.py')
)


def walker(opath='.'):
    # walk the directory tree
    for path, folders, files in walk(opath):
        for filename in files:
            if is_test(filename):
                # get the path minus the origin path
                rpath = relpath(path, opath)

                # build up the import path
                yield 'tests.{}.{}'.format(rpath, splitext(filename)[0])


def suite():
    sys.path = [HERE, MODULE_DIR] + sys.path

    SUB_UNITS = walker(HERE)

    chdir(HERE)

    return unittest.TestLoader().loadTestsFromNames(SUB_UNITS)


def main():
    unittest.TextTestRunner(descriptions=True, verbosity=5).run(
        suite()
    )

if __name__ == '__main__':
    main()
