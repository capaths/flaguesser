from nameko.web.websocket import WebSocketHubProvider, WebSocketHub


class UserSocket:
    users_socket = dict()
    sockets_user = dict()

    def get_user_socket(self, username):
        return self.users_socket[username]

    def get_socket_user(self, socket_id):
        return self.sockets_user[socket_id]

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


class WebSocketHubProviderExt(WebSocketHubProvider):
    user_socket = UserSocket()

    def get_dependency(self, worker_ctx):
        hub = super(WebSocketHubProviderExt, self).get_dependency(worker_ctx)

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

        hub.identify_socket = identify_socket
        hub.get_username = get_username
        hub.get_socket_id = get_socket_id
        hub.get_active_users = get_active_users
        hub.is_identified = is_identified

        return hub

    def cleanup_websocket(self, socket_id):
        self.user_socket.del_socket(socket_id)
        super(WebSocketHubProviderExt, self).cleanup_websocket(socket_id)
