import unittest
import datetime


class TestUtils(unittest.TestCase):
    def test_format_date(self):
        from transperth.jp.location import format_date

        d = datetime.datetime(2014, 2, 13)

        self.assertEqual(
            format_date(d),
            'Thursday, 13 February 2014'
        )

    def test_clean(self):
        from transperth.jp.utils import clean

        ret = clean([
            '    ',
            '\n\t\t',
            'WHAT_WE_WANT'
        ])

        self.assertEqual(
            ret,
            ['WHAT_WE_WANT']
        )

if __name__ == '__main__':
    unittest.main()
