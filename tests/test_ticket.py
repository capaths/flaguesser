import json

import requests
import random
import string

from .utils.socket_connection import SocketConnection

TEST_TITLE = "Título Ticket"
TEST_DESCRIPTION = "Hello, World!"


def test_ticket():
    req = requests.get("localhost:8000/ticket/get")

    req = requests.post("localhost:8000/ticket/all")

    req = requests.get("localhost:8000/ticket/save", json={
        "title": TEST_TITLE,
        "description": TEST_DESCRIPTION
    })
