import unittest


class TestSmartRider(unittest.TestCase):
    def test_smartrider_name_re(self):
        from transperth.smart_rider.smart_rider import SR_NAME_RE

        self.assertEqual(
            SR_NAME_RE.search('Curtin(046038725)').groups(),
            ('Curtin', '046038725')
        )

        self.assertEqual(
            SR_NAME_RE.search('Second high school card(043432897)').groups(),
            ('Second high school card', '043432897')
        )

    def test_stop_re(self):
        from transperth.smart_rider.smart_rider import STOP_RE

        self.assertEqual(
            STOP_RE.search('Canning Bridge St 3').groups(),
            ('3',)
        )

    def test_smart_rider_number_re(self):
        from transperth.smart_rider.smart_rider import SR_NUM_RE

        self.assertEqual(
            SR_NUM_RE.search('046038725').groups(),
            ('0460', '3872', '5')
        )

        self.assertEqual(
            SR_NUM_RE.search('043432897').groups(),
            ('0434', '3289', '7')
        )
