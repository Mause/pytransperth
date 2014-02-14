import unittest
from unittest.mock import Mock


class MockUtilsTestCase(unittest.TestCase):
    def assertEqualMock(self, first, second):
        mock_util = Mock()

        mock_util(first)

        mock_util.assert_called_with(second)
