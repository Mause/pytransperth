import os
import sys
import unittest


def suite():
    MODULE_DIR = os.path.join(os.path.dirname(__file__), '..')
    MODULE_DIR = os.path.abspath(MODULE_DIR)
    sys.path.insert(0, MODULE_DIR)
    sys.path.insert(0, os.path.dirname(__file__))

    SUB_UNITS = os.path.dirname(__file__)
    SUB_UNITS = os.listdir(SUB_UNITS)
    SUB_UNITS = [
        filename[:-3]
        for filename in SUB_UNITS
        if filename.startswith('test_')
    ]

    os.chdir(os.path.dirname(__file__))
    loader = unittest.TestLoader()
    return loader.loadTestsFromNames(SUB_UNITS)
