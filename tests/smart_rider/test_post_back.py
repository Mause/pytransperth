import sys
import unittest

from . import MODULE_DIR
sys.path.insert(0, MODULE_DIR)


class TestPostBack(unittest.TestCase):
    def test_parse_delta(self):
        from transperth.smart_rider.post_back import parse_delta

        delta = parse_delta('7|type|id|content')

        self.assertDictEqual(
            delta,
            {
                'type': [
                    {'id': 'id', 'content': 'content'}
                ]
            }
        )
