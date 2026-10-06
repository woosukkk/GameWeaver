"""Password hashing and opaque session tokens using the standard library."""

import hashlib
import hmac
import secrets
import time
from collections import defaultdict, deque
from threading import Lock


ITERATIONS = 600_000


class RateLimiter:
    def __init__(self, limit=5, window_seconds=300, clock=None):
        self.limit, self.window_seconds = limit, window_seconds
        self.clock = clock or time.monotonic
        self.attempts, self.lock = defaultdict(deque), Lock()

    def allow(self, key):
        now = self.clock()
        with self.lock:
            attempts = self.attempts[key]
            while attempts and attempts[0] <= now - self.window_seconds:
                attempts.popleft()
            if len(attempts) >= self.limit:
                return False
            attempts.append(now)
            return True

    def reset(self, key):
        with self.lock:
            self.attempts.pop(key, None)


def hash_password(password, salt=None):
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("비밀번호는 8자 이상이어야 합니다.")
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password, encoded):
    try:
        algorithm, iterations, salt, expected = encoded.split("$", 3)
        actual = hashlib.pbkdf2_hmac(algorithm.removeprefix("pbkdf2_"), password.encode(), bytes.fromhex(salt), int(iterations))
        return hmac.compare_digest(actual.hex(), expected)
    except (AttributeError, TypeError, ValueError):
        return False


def session_token():
    return secrets.token_urlsafe(32)


def csrf_token():
    return secrets.token_urlsafe(24)


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()
