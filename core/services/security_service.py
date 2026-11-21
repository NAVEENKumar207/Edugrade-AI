"""
Security and rate-limiting service for EduGrade AI.
Provides simple in-memory/cache-based login attempt limiting.
"""

import time
import math
from django.core.cache import cache

MAX_ATTEMPTS = 5
LOCK_SECONDS = 300

def get_fail_key(username: str) -> str:
    return "login_fail_" + username.strip().lower()

def get_lock_key(username: str) -> str:
    return "login_lock_" + username.strip().lower()

def is_account_locked(username: str) -> tuple[bool, int]:
    """
    Checks if username is locked.
    Returns (is_locked, remaining_minutes).
    """
    if not username:
        return False, 0
    clean = username.strip().lower()
    lock_data = cache.get(get_lock_key(clean))
    if lock_data is not None:
        elapsed = time.time() - lock_data
        remaining = max(1, math.ceil((LOCK_SECONDS - elapsed) / 60))
        return True, remaining
    return False, 0

def record_failed_login(username: str) -> tuple[bool, int]:
    """
    Increments failed login counter for a username.
    Locks the username for 300 seconds after 5 failed attempts.
    Returns (is_locked, remaining_minutes).
    """
    if not username:
        return False, 0
    clean = username.strip().lower()
    fail_key = get_fail_key(clean)
    attempts = cache.get(fail_key, 0) + 1
    cache.set(fail_key, attempts, timeout=LOCK_SECONDS)

    if attempts >= MAX_ATTEMPTS:
        cache.set(get_lock_key(clean), time.time(), timeout=LOCK_SECONDS)
        return True, 5
    return False, 0

def reset_login_attempts(username: str):
    """Clears failed attempts counter and lockout status on successful login."""
    if not username:
        return
    clean = username.strip().lower()
    cache.delete(get_fail_key(clean))
    cache.delete(get_lock_key(clean))

def get_lockout_message(remaining_minutes: int = 5) -> str:
    """Standard rate limit error message."""
    return f"Too many failed attempts. Try again in {remaining_minutes} minutes."
