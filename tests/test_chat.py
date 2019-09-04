from .utils.socket_connection import SocketConnection

USER = lambda x: f"TestUser{x}"
ROOM = lambda x: f"Room{x}"
PASS = lambda x: f"secret{x}"

TEST_MESSAGE = "Hello, World!"


def test_sockets():
    # connect
    ws = SocketConnection(f'ws://localhost:8000/ws')

    # try to access method without identification
    assert not ws.send("subscribe_chat")["success"]

    # identify
    assert ws.send('identify', {'username': USER('A')})["success"]

    # access same method as before
    assert ws.send("subscribe_chat")["success"]


def test_chat():
    # connect
    ws_a = SocketConnection(f'ws://localhost:8000/ws')
    ws_b = SocketConnection(f'ws://localhost:8000/ws')

    # identify
    assert ws_a.send('identify', {'username': USER('A')})
    assert ws_b.send('identify', {'username': USER('B')})

    # subscribe to chat
    assert ws_a.send("subscribe_chat")["success"]
    assert ws_b.send("subscribe_chat")["success"]

    # send global message
    assert ws_a.send('process_message', {'content': TEST_MESSAGE})

    result_a = ws_a.recv("event")[0]["data"]
    result_b = ws_b.recv("event")[0]["data"]

    assert result_a["sender"] == USER("A")
    assert result_b["sender"] == USER("A")

    assert result_a["content"] == TEST_MESSAGE
    assert result_b["content"] == TEST_MESSAGE

    # create chat room
    assert ws_a.send("create_room", {
            'sender': USER("A"),
            'room_name': ROOM("A")
    })["success"]

    data = ws_a.recv("event")[0]["data"]
    assert data["room"]["name"] == ROOM("A")
    code_a = data["room"]["code"]

    # subscribe chat room
    assert ws_a.send("subscribe_room", {
            'room_code': code_a
    })["success"]

    # send message in chat room
    assert ws_a.send("process_message", {
            'content': TEST_MESSAGE,
            'room_code': code_a
    })["success"]

    data = ws_a.recv("event")[0]["data"]
    assert data["sender"] == USER('A')
    assert data["content"] == TEST_MESSAGE

    # user outside room shouldn't receive message
    assert len(ws_a.recv("event")) == 0

    # subscribe other user to room
    assert ws_b.send("subscribe_room", {
            'room_code': code_a
    })["success"]

    # send message in chat room
    assert ws_a.send('process_message', {
            'content': TEST_MESSAGE,
            'room_code': code_a
    })["success"]

    # all users in room receive message
    data_a = ws_a.recv("event")[0]["data"]
    data_b = ws_b.recv("event")[0]["data"]

    assert data_a["sender"] == USER('A')
    assert data_a["content"] == TEST_MESSAGE

    assert data_b["sender"] == USER('A')
    assert data_b["content"] == TEST_MESSAGE

    # close connection
    ws_a.close()
    ws_b.close()
