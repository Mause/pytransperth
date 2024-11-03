import unittest


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
