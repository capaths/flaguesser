from .utils import COUNTRIES
from .utils.socket_connection import SocketConnection

import time
import json
import logging

import requests

USER = lambda x: f"TestUser{x}"
PASS = lambda x: f"secret{x}"

TEST_MESSAGE = "Hello, World!"

WS_URL = f'ws://localhost:8000/ws'


def test_challenge():
    ws_a = SocketConnection(WS_URL)
    ws_b = SocketConnection(WS_URL)

    req = requests.get("http://localhost:8000/match/all")
    matches_before = json.loads(req.content)

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

    logging.log(logging.INFO, "match begins")

    assert event_a["data"]["code"] == code
    assert event_b["data"]["code"] == code

    assert event_a["data"]["end_time"] == event_b["data"]["end_time"]
    end_time = event_a["data"]["end_time"]

    # wrong flag guessing
    assert ws_a.send('guess_flag', {
        'guess': "Unexistent Country"
    })["success"]

    assert ws_a.recv("event")[0]["data"]["url"] is None
    assert ws_b.recv("event")[0]["data"]["url"] is None

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
        if event["data"]["guesser"] == USER("A") and event["data"]["url"] is not None:
            score_a += 1

    score_b = 0
    events_b = ws_b.recv("event")
    for event in events_b:
        if event["data"]["guesser"] == USER("B") and event["data"]["url"] is not None:
            score_b += 1

    # check if match ends when reaching end_time
    wait_time = max(0, end_time - time.time()) + 1
    logging.log(logging.INFO, f"waiting {wait_time} seconds to end match")

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

    logging.log(logging.INFO, f"match ends")

    req = requests.get("http://localhost:8000/match/all")
    matches_later = json.loads(req.content)

    assert len(matches_later) - len(matches_before) == 1

    req = requests.get(f"http://localhost:8000/match/byplayer/{USER('A')}")
    matches_a = json.loads(req.content)

    assert matches_a[-1]["id"] == matches_later[-1]["id"]
