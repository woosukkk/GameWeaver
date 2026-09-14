import unittest

from gameweaver.auth import RateLimiter, csrf_token, hash_password, session_token, token_hash, verify_password


class AuthTests(unittest.TestCase):
    def test_password_hash_is_salted_and_verifiable(self):
        first = hash_password("correct horse")
        second = hash_password("correct horse")
        self.assertNotEqual(first, second)
        self.assertTrue(verify_password("correct horse", first))
        self.assertFalse(verify_password("wrong password", first))

    def test_short_password_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "8자"):
            hash_password("short")

    def test_session_token_is_stored_as_hash(self):
        token = session_token()
        self.assertNotEqual(token, token_hash(token))
        self.assertEqual(64, len(token_hash(token)))

    def test_rate_limiter_reopens_after_window(self):
        now = [0]
        limiter = RateLimiter(limit=2, window_seconds=10, clock=lambda: now[0])
        self.assertTrue(limiter.allow("client"))
        self.assertTrue(limiter.allow("client"))
        self.assertFalse(limiter.allow("client"))
        now[0] = 11
        self.assertTrue(limiter.allow("client"))

    def test_csrf_tokens_are_random(self):
        self.assertNotEqual(csrf_token(), csrf_token())


if __name__ == "__main__":
    unittest.main()
