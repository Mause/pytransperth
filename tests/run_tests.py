import os
import sys
import unittest

MODULE_DIR = os.path.join(os.path.dirname(__file__), '..')
MODULE_DIR = os.path.abspath(MODULE_DIR)
sys.path.insert(0, MODULE_DIR)


SUB_UNITS = os.path.dirname(__file__)
SUB_UNITS = os.listdir(SUB_UNITS)
SUB_UNITS = [
    filename[:-3]
    for filename in SUB_UNITS
    if filename.startswith('test_')
]


def main():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(SUB_UNITS)

    runner = unittest.TextTestRunner(verbosity=2)

    end = runner.run(suite)

    if len(end.errors) > 0 or len(end.failures) > 0:
        sys.exit('{} test failures'.format(
            len(end.errors) +
            len(end.failures)
        ))

if __name__ == '__main__':
    main()
