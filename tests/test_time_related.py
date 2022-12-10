from time import sleep
from unittest import TestCase

from src.xlib_commonpy.time_related import TimeoutTimerPassive


class TestTimeoutTimer(TestCase):
    def test_init(self):
        # Normal case
        uut = TimeoutTimerPassive(timeout_time_sec=1)
        self.assertIsNotNone(uut)

        # Zero
        with self.assertRaises(RuntimeError):
            TimeoutTimerPassive(timeout_time_sec=0)

        # Negative
        with self.assertRaises(RuntimeError):
            TimeoutTimerPassive(timeout_time_sec=-1)

    def test_getting_set_limit(self):
        uut = TimeoutTimerPassive(timeout_time_sec=10)
        self.assertEqual(uut.get_timeout_time_sec(), 10)

    def test_is_active(self):
        uut = TimeoutTimerPassive(timeout_time_sec=1)
        self.assertFalse(uut.is_active())

        uut.start_timer()
        self.assertTrue(uut.is_active())

        sleep(1)
        self.assertFalse(uut.is_active())

        uut.reset()
        uut.start_timer()
        self.assertTrue(uut.is_active())

        sleep(1)
        self.assertFalse(uut.is_active())

    def test_starting_timer(self):
        uut = TimeoutTimerPassive(timeout_time_sec=2)
        uut.start_timer()
        sleep(1)
        self.assertTrue(uut.is_active())
        sleep(1)
        self.assertFalse(uut.is_active())

        # Can't start an already started timer
        uut.start_timer()
        with self.assertRaises(RuntimeError):
            uut.start_timer()

    def test_timing_out(self):
        uut = TimeoutTimerPassive(timeout_time_sec=2)

        # Technically, timeouts never occur on init or after a fresh reset
        self.assertFalse(uut.timed_out())

        for _ in range(2):
            uut.start_timer()
            sleep(1)
            # No timeout yet
            self.assertFalse(uut.timed_out())
            sleep(1)
            # Should have timed out
            self.assertTrue(uut.timed_out())

        # Timing out via exception
        uut = TimeoutTimerPassive(timeout_time_sec=1)
        uut.start_timer()
        with self.assertRaises(RuntimeError):
            sleep(1)
            uut.timed_out(raise_on_timeout=True)

    def test_reset(self):
        uut = TimeoutTimerPassive(timeout_time_sec=100)
        for _ in range(2):
            uut.start_timer()
            self.assertTrue(uut.is_active())
            uut.reset()
            self.assertFalse(uut.is_active())
