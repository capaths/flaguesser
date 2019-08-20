from flask_socketio import send, emit, join_room


def prepare_sockets(socketio):

    @socketio.on("sendChatMessage")
    def receive_message(data):
        emit("receiveMessage", data, room="all")

    @socketio.on("connect")
    def on_connection():
        join_room("all")
