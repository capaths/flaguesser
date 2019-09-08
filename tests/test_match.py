import requests

from .utils import COUNTRIES
from .utils.socket_connection import SocketConnection

import time

USER = lambda x: f"TestUser{x}"
PASS = lambda x: f"secret{x}"

TEST_MESSAGE = "Hello, World!"

WS_URL = f'ws://localhost:8000/ws'


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
    assert req.json()[0] == USER('A')

    # identify two sockets more
    assert ws_b.send('identify', {'username': USER('B')})["success"]
    assert ws_c.send('identify', {'username': USER('C')})["success"]

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
    ws_a = SocketConnection(WS_URL)
    ws_b = SocketConnection(WS_URL)

    # identify sockets
    assert ws_a.send('identify', {'username': USER('A')})["success"]
    assert ws_b.send('identify', {'username': USER('B')})["success"]

    # challenge user A to B
    assert ws_a.send('challenge', {'challenged': USER('B')})["success"]
    challenge_b = ws_b.recv('event')[0]["data"]
    assert challenge_b["sender"] == USER('A')

    code = challenge_b["code"]

    # accept challenge with a wrong code
    assert not ws_b.send('accept_challenge', {
        'challenger': USER('A'),
        'code': 'wrong',
        'start_time': challenge_b["start_time"]
    })["success"]

    # accept challenge with the code
    assert ws_b.send('accept_challenge', {
        'challenger': USER('A'),
        'start_time': challenge_b["start_time"],
        'code': code
    })["success"]

    event_b = ws_b.recv("event")[0]
    event_a = ws_a.recv("event")[0]
    assert event_b["event"] == "match_begins"
    assert event_a["event"] == "match_begins"

    assert event_a["data"]["code"] == code
    assert event_b["data"]["code"] == code

    assert event_a["data"]["end_time"] == event_b["data"]["end_time"]
    end_time = event_a["data"]["end_time"]

    # wrong flag guessing
    assert ws_a.send('guess_flag', {
        'guess': "Unexistent Country"
    })["success"]

    assert not ws_a.recv("event")[0]["data"]["right"]
    assert not ws_b.recv("event")[0]["data"]["right"]

    import random
    random.seed(code)
    test_countries = random.sample(COUNTRIES, 10)

    # many flag guessing
    for country in test_countries[:5]:
        assert ws_a.send('guess_flag', {
            'guess': country
        })["success"]

    for country in test_countries[5:]:
        assert ws_b.send('guess_flag', {
            'guess': country
        })["success"]

    score_a = 0
    events_a = ws_a.recv("event")
    for event in events_a:
        if event["data"]["guesser"] == USER("A") and event["data"]["right"]:
            score_a += 1

    score_b = 0
    events_b = ws_b.recv("event")
    for event in events_b:
        if event["data"]["guesser"] == USER("B") and event["data"]["right"]:
            score_b += 1

    # check if match ends when reaching end_time
    wait_time = max(0, end_time - time.time()) + 1
    time.sleep(wait_time)

    last_events_a = events_a + ws_a.recv("event")
    last_events_b = events_b + ws_b.recv("event")

    end_match_a = None
    for event in last_events_a:
        if event["event"] == "end_match":
            end_match_a = event["data"]

    end_match_b = None
    for event in last_events_b:
        if event["event"] == "end_match":
            end_match_b = event["data"]

    assert end_match_a is not None
    assert end_match_b is not None

    # disconnect
    ws_a.close()
    ws_b.close()
