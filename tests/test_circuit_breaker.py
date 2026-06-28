import time
import unittest

from app.resilience.circuit_breaker import CircuitBreaker, CircuitState


class CircuitBreakerTests(unittest.TestCase):
    def test_opens_after_threshold_and_recovers_half_open(self):
        breaker = CircuitBreaker("test", failure_threshold=2, recovery_timeout_seconds=0.01)
        self.assertTrue(breaker.allow_request())
        breaker.record_failure("one")
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        breaker.record_failure("two")
        self.assertEqual(breaker.state, CircuitState.OPEN)
        self.assertFalse(breaker.allow_request())
        time.sleep(0.02)
        self.assertTrue(breaker.allow_request())
        self.assertEqual(breaker.state, CircuitState.HALF_OPEN)
        breaker.record_success()
        self.assertEqual(breaker.state, CircuitState.CLOSED)


if __name__ == "__main__":
    unittest.main()
