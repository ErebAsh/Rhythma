import sys
import os
import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.sms import SMSSettings


def test_sms_settings_phone_validation():
    # Valid E.164 phone
    valid_settings = SMSSettings(phoneNumber="+919876543210", enabled=False)
    assert valid_settings.normalized_phone == "+919876543210"

    # Empty phone string allowed
    empty_settings = SMSSettings(phoneNumber="", enabled=False)
    assert empty_settings.normalized_phone is None

    # Invalid phone format raises ValidationError
    with pytest.raises(ValidationError):
        SMSSettings(phoneNumber="invalid_12345", enabled=False)
