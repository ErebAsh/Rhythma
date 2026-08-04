import sys
import os
from datetime import date, timedelta
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.sms import generate_cycle_sms_summary


def test_generate_cycle_sms_summary_formatting():
    # Verify generated SMS summary is valid string under 160 chars
    summary = generate_cycle_sms_summary("test_mock_user_id")
    assert isinstance(summary, str)
    assert len(summary) <= 160
    assert "Rhythma Summary" in summary
    assert "Next period expected" in summary
