import json

import requests
import random
import string

from .utils.socket_connection import SocketConnection

WS_URL = f'ws://localhost:8000/ws'

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

        req = requests.post(url, json=payload, timeout=20)
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

    req = requests.get(f"http://localhost:8000/player/{USER('A')}")
    assert req.json()["username"] == USER('A')


def test_identification():
    ws_a = SocketConnection(WS_URL)
    ws_b = SocketConnection(WS_URL)
    ws_c = SocketConnection(WS_URL)

    # get online users without identified users
    req = requests.get("http://localhost:8000/online_users")
    assert len(req.json()) == 0

    # identify one socket
    assert ws_a.send('identify', {'username': USER('A')})["success"]

    # get online users with one identified user
    req = requests.get("http://localhost:8000/online_users")
    assert len(req.json()) == 1
    assert req.json()[USER('A')]["username"] == USER('A')

    # identify one more socket
    assert ws_c.send('identify', {'username': USER('C')})["success"]

    # identify other socket via request that needs id
    assert ws_b.send('subscribe_chat', {
        'username': USER('B')
    })["success"]

    # get online users with three identified users
    req = requests.get("http://localhost:8000/online_users")
    assert len(req.json()) == 3

    # disconnect one
    ws_c.close()

    req = requests.get("http://localhost:8000/online_users")
    assert len(req.json()) == 2

    ws_a.close()
    ws_b.close()
