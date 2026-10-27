import unittest

import lxml.html


class XMLTestCase(unittest.TestCase):
    def assertEqualXML(self, first, second) -> None:
        self.assertEqual(lxml.html.tostring(first), lxml.html.tostring(second))
