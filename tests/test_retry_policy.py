import unittest

from app.resilience.retry_policy import RetryPolicy


class RetryPolicyTests(unittest.TestCase):
    def test_retries_until_success(self):
        policy = RetryPolicy(max_attempts=3, base_delay_seconds=0, jitter_seconds=0)
        calls = {"count": 0}

        def fn():
            calls["count"] += 1
            if calls["count"] < 2:
                raise RuntimeError("temporary")
            return "ok"

        self.assertEqual(policy.run(fn), "ok")
        self.assertEqual(calls["count"], 2)

    def test_raises_last_error(self):
        policy = RetryPolicy(max_attempts=2, base_delay_seconds=0, jitter_seconds=0)
        with self.assertRaisesRegex(RuntimeError, "boom"):
            policy.run(lambda: (_ for _ in ()).throw(RuntimeError("boom")))


if __name__ == "__main__":
    unittest.main()
