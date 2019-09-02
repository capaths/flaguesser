import json

import pytest
import requests
import time

from nameko.testing.services import worker_factory
from websocket import create_connection, WebSocketTimeoutException

USER = lambda x: f"TestUser{x}"
PASS = lambda x: f"secret{x}"

TEST_MESSAGE = "Hello, World!"


def test_signup():
    # signup with users
    for user_tag in ["A", "B", "C"]:
        url = 'http://localhost:8000/signup'

        payload = {
            'username': USER(user_tag),
            'password': PASS(user_tag)
        }

        req = requests.post(url, json=payload)
        data = json.loads(req.content)

        assert req.status_code == 200
        assert data["user"]["username"] == USER(user_tag)

    # signup with used username
    req = requests.post(url, json=payload)
    assert req.status_code == 500
