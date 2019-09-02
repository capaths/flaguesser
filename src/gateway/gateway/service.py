""" Gateway """
import json

from nameko.rpc import RpcProxy
from nameko.web.handlers import http
from nameko.exceptions import BadRequest
from nameko.extensions import DependencyProvider

from nameko.web.websocket import rpc as srpc

from marshmallow import ValidationError

from gateway.sockets import WebSocketHubProviderExt
from gateway.schemas import LoginSchema
from gateway.cors_http import cors_http


class Config(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return self.container.config


class ContainerIdentifier(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return id(self.container)


class GatewayService:
    """
    Gateway for other services
    """

    name = "gateway"

    hub = WebSocketHubProviderExt()

    config = Config()

    container_id = ContainerIdentifier()

    def set_in_socket(self, socket_id, item, value):
        self.hub._get_connection(socket_id).context_data[item] = value

    def get_from_socket(self, socket_id, item):
        data = self.hub._get_connection(socket_id).context_data
        return data.get(item)

    auth = RpcProxy('access')

    ticket_rpc = RpcProxy('ticket')
    chat_rpc = RpcProxy('chat')
    match_rpc = RpcProxy('match')
    player_rpc = RpcProxy('player')

    @cors_http("GET", "/ticket")
    def get_ticket(self, request):
        return self.ticket_rpc.get_ticket("user")

    @cors_http("POST", "/login")
    def login(self, request):
        schema = LoginSchema(strict=True)

        try:
            login_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            return 400, f"Not valid JSON: {exc}"
        except ValidationError as exc:
            return 400, f"Not valid arguments: {exc}"

        username = login_data["username"]
        password = login_data["password"]

        user_data = self.auth.login(username, password)
        if user_data:
            return 200, user_data
        return 400, "Invalid credentials"

    @cors_http("POST", "/signup")
    def signup(self, request):
        schema = LoginSchema(strict=True)

        try:
            login_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        username = login_data["username"]
        password = login_data["password"]

        if self.auth.signup(username, password):
            user_data = self.auth.login(username, password)
            if user_data:
                return 200, user_data
            return 500, "Something went wrong"
        else:
            return 500, "User already exists"

    @srpc
    def identify(self, socket_id, username):
        self.hub.identify_socket(socket_id, username)

    @srpc
    def subscribe_chat(self, socket_id):
        if not self.hub.is_identified(socket_id):
            raise PermissionError("Not identified connection")
        else:
            self.hub.subscribe(socket_id, 'chat')

    @srpc
    def subscribe_challenge(self, socket_id):
        if not self.hub.is_identified(socket_id):
            self.hub.subscribe(socket_id, 'challenge')
            return True
        return False

    # Chat

    @srpc
    def create_room(self, socket_id, sender, room_name):
        room_code = self.chat_rpc.create_room(room_name, sender)

        if room_code is None:
            raise ValueError(f"Player {sender} does not exist")

        self.hub.unicast(socket_id, 'room_data', json.loads(room_code))

    @srpc
    def subscribe_room(self, socket_id, room_code):
        self.hub.subscribe(socket_id, room_code)

    @srpc
    def unsubscribe_room(self, socket_id, room_code):
        self.hub.unsubscribe(socket_id, room_code)

    @srpc
    def process_message(self, socket_id, content, room_code=None):
        username = self.hub.get_username(socket_id)
        if username is None:
            raise PermissionError("Not identified connection")

        if not self.chat_rpc.validate_message(username, content):
            raise ValueError("Not valid message")

        channel = 'chat' if room_code is None else room_code

        self.hub.broadcast(channel, 'new_message', {
            "sender": username,
            "content": content
        })

    # Match
    @http("GET", "/online_users")
    def get_connected_users(self, request):
        return json.dumps(self.hub.get_active_users())

    @srpc
    def challenge(self, socket_id, challenged):
        username = self.hub.get_username(socket_id)

        if username is None:
            raise PermissionError("Not identified connection")

        code = self.match_rpc.generate_match(username, challenged)
        self.hub.unicast(self.hub.get_socket_id(challenged), 'challenge', {
            "sender": username,
            "code": code["code"],
            "flags": code["flags"]
        })

    @srpc
    def accept_challenge(self, socket_id, challenger, code, flags):
        challenged = self.hub.get_username(socket_id)
        if challenged is None:
            raise PermissionError("Not identified connection")

        real_code = self.match_rpc.generate_match(challenger, challenged)["code"]
        if code != real_code:
            raise ValueError(f"Invalid challenge code")

        socket_id_b = self.hub.get_socket_id(challenger)
        if socket_id_b is None:
            raise ValueError("Challenger doesn't exist")

        match_channel = f"match;{code}"
        self.hub.subscribe(socket_id, match_channel)
        self.hub.subscribe(socket_id_b, match_channel)

        self.hub.broadcast(match_channel, "match_begins", {
            "code": code,
            "flags": flags
        })

    @srpc
    def guess_flag(self, socket_id, code, guess):
        match_channel = f"match;{code}"
        self.hub.broadcast(match_channel, "guess", {
            "guess": guess,
            "right": self.match_rpc.guess_flag(code, guess)
        })
