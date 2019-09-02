import json

import pytest
import requests
import time

from nameko.testing.services import worker_factory
from websocket import create_connection, WebSocketTimeoutException

USER = lambda x: f"TestUser{x}"
PASS = lambda x: f"secret{x}"

TEST_MESSAGE = "Hello, World!"

WS_URL = f'ws://localhost:8000/ws'


def test_identification():
    ws_a = create_connection(WS_URL)
    ws_b = create_connection(WS_URL)
    ws_c = create_connection(WS_URL)

    # get online users without identified users
    req = requests.get("http://localhost:8000/online_users")
    assert len(req.json()) == 0

    # identify one socket
    ws_a.send(json.dumps({
        'method': 'identify',
        'data': {
            'username': USER('A')
        }
    }))

    # get online users with one identified user
    req = requests.get("http://localhost:8000/online_users")
    assert len(req.json()) == 1
    assert req.json()[0] == USER('A')

    # identify two sockets more
    ws_b.send(json.dumps({
        'method': 'identify',
        'data': {
            'username': USER('B')
        }
    }))

    ws_c.send(json.dumps({
        'method': 'identify',
        'data': {
            'username': USER('C')
        }
    }))

    # get online users with three identified users
    req = requests.get("http://localhost:8000/online_users")
    assert len(req.json()) == 3

    # disconnect one
    ws_c.close()
    req = requests.get("http://localhost:8000/online_users")
    assert len(req.json()) == 2

    ws_a.close()
    ws_b.close()


def test_challenge():
    ws_a = create_connection(WS_URL)
    ws_b = create_connection(WS_URL)
    ws_c = create_connection(WS_URL)

    ws_a.settimeout(1)
    ws_b.settimeout(1)
    ws_c.settimeout(1)

    ws_a.recv()
    ws_b.recv()
    ws_c.recv()

    # identify sockets
    ws_a.send(json.dumps({
        'method': 'identify',
        'data': {
            'username': USER('A')
        }
    }))

    ws_b.send(json.dumps({
        'method': 'identify',
        'data': {
            'username': USER('B')
        }
    }))

    ws_c.send(json.dumps({
        'method': 'identify',
        'data': {
            'username': USER('C')
        }
    }))

    ws_a.recv()
    ws_b.recv()
    ws_c.recv()

    # challenge user A to B
    ws_a.send(json.dumps({
        'method': 'challenge',
        'data': {
            'challenged': USER('B')
        }
    }))

    ws_a.recv()

    try:
        data_b = ws_b.recv()
    except WebSocketTimeoutException:
        assert False

    challenge_b = json.loads(data_b)["data"]
    assert challenge_b["sender"] == USER('A')

    code = challenge_b["code"]
    flags = challenge_b["flags"]

    # accept challenge with a wrong code
    ws_b.send(json.dumps({
        'method': 'accept_challenge',
        'data': {
            'challenger': USER('A'),
            'code': "wrong"
        }
    }))

    assert not json.loads(ws_b.recv())["success"]

    # accept challenge with the code
    ws_b.send(json.dumps({
        'method': 'accept_challenge',
        'data': {
            'challenger': USER('A'),
            'code': code,
            'flags': flags
        }
    }))

    match_b = json.loads(ws_b.recv())
    assert match_b["event"] == "match_begins"

    match_a = json.loads(ws_a.recv())
    assert match_a["event"] == "match_begins"

    ws_b.recv()

    # wrong flag guessing
    ws_a.send(json.dumps({
        'method': 'guess_flag',
        'data': {
            'code': code,
            'guess': "Unexistent Country"
        }
    }))

    assert not json.loads(ws_a.recv())["data"]["right"]
    assert not json.loads(ws_b.recv())["data"]["right"]

    ws_a.recv()

    # right flag guessing
    ws_a.send(json.dumps({
        'method': 'guess_flag',
        'data': {
            'code': code,
            'guess': flags[0]["name"]
        }
    }))

    assert json.loads(ws_a.recv())["data"]["right"]
    assert json.loads(ws_b.recv())["data"]["right"]

    # send end signal
    ws_a.send(json.dumps({
        'method': 'end_match',
        'data': {
            'code': code,
            'guess': flags[0]["name"]
        }
    }))

    # disconnect
    ws_a.close()
    ws_b.close()
    ws_c.close()
