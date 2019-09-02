import json

import pytest
import requests
import time

from nameko.testing.services import worker_factory
from websocket import create_connection, WebSocketTimeoutException

USER = lambda x: f"TestUser{x}"
ROOM = lambda x: f"Room{x}"
PASS = lambda x: f"secret{x}"

TEST_MESSAGE = "Hello, World!"


def test_sockets():
    # connect
    ws = create_connection(f'ws://localhost:8000/ws')
    assert json.loads(ws.recv())["event"] == "connected"

    # try to access method without identification
    ws.send(json.dumps({
        'method': 'subscribe_chat'
    }))

    assert not json.loads(ws.recv())["success"]

    # identify
    ws.send(json.dumps({
        'method': 'identify',
        'data': {
            'username': USER('A')
        }
    }))

    # access same method as before
    ws.send(json.dumps({
        'method': 'subscribe_chat'
    }))

    assert json.loads(ws.recv())["success"]

def test_chat():
    # connect
    ws_a = create_connection(f'ws://localhost:8000/ws')
    ws_b = create_connection(f'ws://localhost:8000/ws')

    ws_a.settimeout(0.5)
    ws_b.settimeout(0.5)

    ws_a.recv()
    ws_b.recv()

    # identify
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

    # subscribe to chat
    payload = {
        'method': 'subscribe_chat'
    }

    ws_a.send(json.dumps(payload))
    ws_b.send(json.dumps(payload))

    result_a = json.loads(ws_a.recv())
    result_b = json.loads(ws_b.recv())
    assert result_a["success"]
    assert result_b["success"]

    # send global message
    payload = {
        'method': 'process_message',
        'data': {
            'content': TEST_MESSAGE
        }
    }

    ws_a.send(json.dumps(payload))
    ws_a.recv()
    ws_b.recv()

    data_a = json.loads(ws_a.recv())
    print(data_a)
    result_a = data_a["data"]
    result_b = json.loads(ws_b.recv())["data"]

    assert result_a["sender"] == USER("A")
    assert result_b["sender"] == USER("A")

    assert result_a["content"] == TEST_MESSAGE
    assert result_b["content"] == TEST_MESSAGE

    ws_a.recv()

    # create chat room
    payload = {
        'method': 'create_room',
        'data': {
            'sender': USER("A"),
            'room_name': ROOM("A")
        }
    }
    ws_a.send(json.dumps(payload))
    data = json.loads(ws_a.recv())["data"]
    assert data["room"]["name"] == ROOM("A")
    code_a = data["room"]["code"]

    ws_a.recv()

    # subscribe chat room
    payload = {
        'method': 'subscribe_room',
        'data': {
            'room_code': code_a
        }
    }
    ws_a.send(json.dumps(payload))
    data = json.loads(ws_a.recv())
    assert data["success"]

    # send message in chat room
    payload = {
        'method': 'process_message',
        'data': {
            'content': TEST_MESSAGE,
            'room_code': code_a
        }
    }
    ws_a.send(json.dumps(payload))

    data = json.loads(ws_a.recv())

    assert data["data"]["sender"] == USER('A')
    assert data["data"]["content"] == TEST_MESSAGE

    # user outside room shouldn't receive message

    try:
        ws_b.recv()
        assert False
    except WebSocketTimeoutException:
        assert True

    # subscribe other user to room
    payload = {
        'method': 'subscribe_room',
        'data': {
            'room_code': code_a
        }
    }
    ws_b.send(json.dumps(payload))
    data = json.loads(ws_b.recv())
    assert data["success"]

    # send message in chat room
    payload = {
        'method': 'process_message',
        'data': {
            'content': TEST_MESSAGE,
            'room_code': code_a
        }
    }
    ws_a.send(json.dumps(payload))
    ws_a.recv()

    data_a = json.loads(ws_a.recv())
    data_b = json.loads(ws_b.recv())

    assert data_a["data"]["sender"] == USER('A')
    assert data_a["data"]["content"] == TEST_MESSAGE

    assert data_b["data"]["sender"] == USER('A')
    assert data_b["data"]["content"] == TEST_MESSAGE

    ws_a.close()
    ws_b.close()
