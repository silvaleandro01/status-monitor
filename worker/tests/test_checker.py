from unittest.mock import MagicMock, patch

import requests

from checker import check_service


def test_check_service_up():
    fake_response = MagicMock(status_code=200)
    with patch("checker.requests.get", return_value=fake_response):
        result = check_service("https://exemplo-qualquer.com")

    assert result["status"] == "up"
    assert result["status_code"] == 200
    assert result["error_message"] is None
    assert isinstance(result["response_time_ms"], int)


def test_check_service_http_error_status():
    fake_response = MagicMock(status_code=500)
    with patch("checker.requests.get", return_value=fake_response):
        result = check_service("https://exemplo-qualquer.com")

    assert result["status"] == "down"
    assert result["status_code"] == 500


def test_check_service_connection_error():
    with patch("checker.requests.get", side_effect=requests.exceptions.ConnectionError("boom")):
        result = check_service("https://exemplo-qualquer.com")

    assert result["status"] == "down"
    assert result["status_code"] is None
    assert "boom" in result["error_message"]
