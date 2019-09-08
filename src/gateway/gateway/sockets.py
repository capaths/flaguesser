import time

from nameko.web.websocket import WebSocketHubProvider, WebSocketHub


class UserSocket:
    users_socket = dict()
    sockets_user = dict()

    def get_user_socket(self, username):
        return self.users_socket.get(username)

    def get_socket_user(self, socket_id):
        return self.sockets_user.get(socket_id)

    def clean(self, username, socket_id):
        old_socket_id = self.users_socket.get(username)
        if old_socket_id:
            self.del_socket(old_socket_id)

        old_username = self.sockets_user.get(socket_id)
        if old_username:
            self.del_username(old_username)

    def set_user_socket(self, username, socket_id):
        self.clean(username, socket_id)
        self.users_socket[username] = socket_id
        self.sockets_user[socket_id] = username

    def set_socket_user(self, socket_id, username):
        self.clean(username, socket_id)
        self.sockets_user[socket_id] = username
        self.users_socket[username] = socket_id

    def del_socket(self, socket_id):
        username = self.sockets_user.get(socket_id)
        if not username:
            return
        del self.users_socket[username]
        del self.sockets_user[socket_id]

    def del_username(self, username):
        socket_id = self.users_socket.get(username)
        if not socket_id:
            return
        del self.sockets_user[socket_id]
        del self.users_socket[username]


class SocketMatches:
    active_matches = dict()
    socket_matches = dict()

    def set_active_match(self, code, socket_id1, socket_id2, end_time):
        self.pop_match(socket_id1)
        self.pop_match(socket_id2)

        self.socket_matches[socket_id1] = [(code, socket_id2), 0]
        self.socket_matches[socket_id2] = [(code, socket_id1), 0]
        self.active_matches[code] = (socket_id1, socket_id2, end_time)

    def get_match_by_socket(self, socket_id):
        match_score = self.socket_matches.get(socket_id)
        if match_score is None:
            return

        match, score_a = match_score

        code, socket_id_b = match[0], match[1]
        end_time = self.active_matches[code][2]
        score_b = self.socket_matches[socket_id_b][1]
        return {
            "code": code,
            "end_time": end_time,
            "player1": {
                "socket_id": socket_id,
                "score": score_a
            },
            "player2": {
                "socket_id": socket_id_b,
                "score": score_b
            }
        }

    def get_socket_score(self, socket_id):
        return self.socket_matches[socket_id][1]

    def get_match_by_code(self, code):
        socket_id1 = self.active_matches[code][0]
        return self.get_match_by_socket(socket_id1)

    def pop_match(self, socket_id):
        match = self.get_match_by_socket(socket_id)
        if match is None:
            return

        code = match["code"]
        socket_id_b = match["player2"]["socket_id"]

        del self.socket_matches[socket_id]
        del self.socket_matches[socket_id_b]
        del self.active_matches[code]

        return match

    def pop_match_by_code(self, code):
        socket_id = self.get_match_by_code(code)["player1"]["socket_id"]
        return self.pop_match(socket_id)

    def give_point(self, socket_id):
        score = self.socket_matches[socket_id][1]
        self.socket_matches[socket_id][1] = score + 1
        return score + 1

    def get_timed_out_matches(self):
        current_time = time.time()
        return [self.get_match_by_code(code) for code, match in self.active_matches.items() if current_time > match[2]]


class WebSocketHubProviderExt(WebSocketHubProvider):
    user_socket = UserSocket()
    socket_matches = SocketMatches()
    registered_rooms = list()

    def get_dependency(self, worker_ctx):
        hub = super(WebSocketHubProviderExt, self).get_dependency(worker_ctx)

        # identification
        def identify_socket(socket_id, username):
            self.user_socket.set_user_socket(username, socket_id)

        def get_username(socket_id):
            return self.user_socket.get_socket_user(socket_id)

        def get_socket_id(username):
            return self.user_socket.get_user_socket(username)

        def is_identified(socket_id):
            return self.user_socket.get_socket_user(socket_id) is not None

        def get_active_users():
            return list(self.user_socket.users_socket.keys())

        def register_room(room_code):
            self.registered_rooms.append(room_code)

        def subscribe_room(socket_id, room_code):
            if is_valid_room(room_code):
                hub.subscribe(socket_id, f"chat;{room_code}")
            else:
                raise ValueError("Not valid room code")

        def is_valid_room(room_code):
            return room_code in self.registered_rooms

        hub.identify_socket = identify_socket
        hub.get_username = get_username
        hub.get_socket_id = get_socket_id
        hub.get_active_users = get_active_users
        hub.is_identified = is_identified
        hub.subscribe_room = subscribe_room
        hub.is_valid_room = is_valid_room
        hub.register_room = register_room

        # matches
        def get_match(socket_id):
            return self.socket_matches.get_match_by_socket(socket_id)

        def give_point(socket_id):
            return self.socket_matches.give_point(socket_id)

        def get_timed_out_matches():
            return self.socket_matches.get_timed_out_matches()

        def begin_match(code, socket_id1, socket_id2):
            end_time = time.time() + 30
            self.socket_matches.set_active_match(code, socket_id1, socket_id2, end_time)

        def pop_match(code):
            return self.socket_matches.pop_match_by_code(code)

        hub.get_match = get_match
        hub.begin_match = begin_match
        hub.give_point = give_point
        hub.get_timed_out_matches = get_timed_out_matches
        hub.pop_match = pop_match

        return hub

    def cleanup_websocket(self, socket_id):
        self.user_socket.del_socket(socket_id)
        self.socket_matches.pop_match(socket_id)
        super(WebSocketHubProviderExt, self).cleanup_websocket(socket_id)
