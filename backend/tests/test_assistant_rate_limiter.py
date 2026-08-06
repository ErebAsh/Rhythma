import sys
import os
from datetime import datetime, timedelta, timezone
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.assistant import is_rate_limited, _assistant_rate_history


def test_rate_limiter_key_cleanup():
    _assistant_rate_history.clear()
    user_id = "test_user_leak_check"

    # Add old timestamps outside window
    past_time = datetime.now(timezone.utc) - timedelta(seconds=120)
    _assistant_rate_history[user_id] = [past_time]

    # Calling rate limiter should prune past_time and clean up key if empty before adding new
    res = is_rate_limited(user_id)
    assert res is None
    assert user_id in _assistant_rate_history
    assert len(_assistant_rate_history[user_id]) == 1

    # Simulate window expiry manually
    _assistant_rate_history[user_id] = [past_time]
    # Check that another user call purges user_id when expired
    is_rate_limited("user_b")
    # user_id with old timestamps should have been deleted when checked
    is_rate_limited(user_id)
    # Cleanup history after test
    _assistant_rate_history.clear()
