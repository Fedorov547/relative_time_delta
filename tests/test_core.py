import unittest
from datetime import date, datetime

from relative_time_delta import resolve


class TestResolve(unittest.TestCase):

    def test_third_wednesday_basic(self):
        # 2024-06-01 is a Saturday. Third Wednesday is the 19th.
        base = date(2024, 6, 1)
        result = resolve("third Wednesday", base)
        self.assertEqual(result, datetime(2024, 6, 19, 0, 0, 0))

    def test_third_monday_january_2024(self):
        # 2024-01-01 is a Monday, so third Monday is the 15th.
        base = date(2024, 1, 1)
        result = resolve("third Monday", base)
        self.assertEqual(result, datetime(2024, 1, 15, 0, 0, 0))

    def test_third_friday_february_2024_leap(self):
        # 2024-02-01 is a Thursday. First Friday is the 2nd, third is the 16th.
        base = date(2024, 2, 1)
        result = resolve("third Friday", base)
        self.assertEqual(result, datetime(2024, 2, 16, 0, 0, 0))

    def test_last_monday_of_march_from_january(self):
        # 2024-03 has its last Monday on the 25th.
        base = date(2024, 1, 15)
        result = resolve("last Monday of March", base)
        self.assertEqual(result, datetime(2024, 3, 25, 0, 0, 0))

    def test_last_friday_of_february_2024_leap(self):
        # 2024-02 is a leap year. Last day is the 29th (Thursday).
        # Last Friday is the 23rd.
        base = date(2024, 2, 1)
        result = resolve("last Friday of February", base)
        self.assertEqual(result, datetime(2024, 2, 23, 0, 0, 0))

    def test_last_monday_of_march_rolls_to_next_year(self):
        # Base is November 2024; March 2024 has already passed, so we
        # expect March 2025 (last Monday is the 31st).
        base = date(2024, 11, 1)
        result = resolve("last Monday of March", base)
        self.assertEqual(result, datetime(2025, 3, 31, 0, 0, 0))

    def test_last_monday_simple_previous_week(self):
        # 2024-06-05 is a Wednesday. Last Monday is the 3rd.
        base = date(2024, 6, 5)
        result = resolve("last Monday", base)
        self.assertEqual(result, datetime(2024, 6, 3, 0, 0, 0))

    def test_last_tuesday_previous_week(self):
        # 2024-06-05 is a Wednesday. Last Tuesday is the 4th.
        base = date(2024, 6, 5)
        result = resolve("last Tuesday", base)
        self.assertEqual(result, datetime(2024, 6, 4, 0, 0, 0))

    def test_last_saturday_distant(self):
        # 2024-06-05 is a Wednesday. Last Saturday is the 1st.
        base = date(2024, 6, 5)
        result = resolve("last Saturday", base)
        self.assertEqual(result, datetime(2024, 6, 1, 0, 0, 0))

    def test_last_friday_same_day_is_previous_week(self):
        # 2024-06-07 is a Friday. "Last Friday" on the same day yields
        # the previous week's Friday, the 31st of May, not today.
        base = date(2024, 6, 7)
        result = resolve("last Friday", base)
        self.assertEqual(result, datetime(2024, 5, 31, 0, 0, 0))

    def test_unknown_phrase_raises(self):
        base = date(2024, 6, 5)
        with self.assertRaises(ValueError):
            resolve("second to last Tuesday", base)

    def test_unknown_day_raises(self):
        base = date(2024, 6, 5)
        with self.assertRaises(ValueError):
            resolve("third Funday", base)

    def test_accepts_datetime_base(self):
        base = datetime(2024, 6, 5, 10, 30, 0)
        result = resolve("last Monday", base)
        self.assertEqual(result, datetime(2024, 6, 3, 0, 0, 0))

    def test_phrase_case_insensitive(self):
        base = date(2024, 6, 5)
        result = resolve("LAST monday", base)
        self.assertEqual(result, datetime(2024, 6, 3, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
