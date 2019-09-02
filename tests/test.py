import json

import requests
import random
import string

USER = lambda x: f"TestUser{x}"
PASS = lambda x: f"secret{x}"

TEST_MESSAGE = "Hello, World!"


def random_username(length=20):
    chars = string.ascii_letters + string.digits
    return ''.join([random.choice(chars) for _ in range(length)])


def test_signup():
    # signup with users
    url = 'http://localhost:8000/signup'

    for _ in range(3):
        username = random_username()

        payload = {
            'username': username,
            'password': "secret"
        }

        req = requests.post(url, json=payload)
        data = json.loads(req.content)

        assert req.status_code == 200
        assert data["user"]["username"] == username

    # test users
    payload_a = {
        'username': USER("A"),
        'password': "secret"
    }

    payload_b = {
        'username': USER("B"),
        'password': "secret"
    }

    payload_c = {
        'username': USER("C"),
        'password': "secret"
    }

    requests.post(url, json=payload_a)
    requests.post(url, json=payload_b)
    requests.post(url, json=payload_c)

    # signup with used username
    req = requests.post(url, json=payload_a)
    assert req.status_code == 500
