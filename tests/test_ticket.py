import json

import requests
import random
import string

from .utils.socket_connection import SocketConnection

TEST_TITLE = "Titulo Ticket"
TEST_DESCRIPTION = "Hello, World!"


def test_ticket():
    req = requests.post("localhost:8000/save", json={
        "title": TEST_TITLE,
        "description": TEST_DESCRIPTION
    })

    req = requests.get("localhost:8000/all")

    assert len(req.json()) >= 1
