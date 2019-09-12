from .utils.socket_connection import SocketConnection

USER = lambda x: f"TestUser{x}"
ROOM = lambda x: f"Room{x}"
PASS = lambda x: f"secret{x}"

TEST_MESSAGE = "Hello, World!"


def test_sqli():
    # connect
    ws = SocketConnection(f'ws://localhost:8000/ws')

    # try to access method without identification
    assert not ws.send("subscribe_chat")["success"]

    # identify
    assert ws.send('identify', {'username': USER('A')})["success"]

    # access same method as before
    assert ws.send("subscribe_chat")["success"]
