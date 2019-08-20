""" Gateway """
from __future__ import absolute_import

from nameko.rpc import RpcProxy, rpc
from nameko.web.handlers import http
from nameko.exceptions import BadRequest, RemoteError
from nameko.extensions import DependencyProvider

from nameko.web.websocket import WebSocketHubProvider
from nameko.web.websocket import rpc as srpc

from gateway.schemas import LoginSchema


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

    hub = WebSocketHubProvider()

    config = Config()
    container_id = ContainerIdentifier()

    auth = RpcProxy('access')

    ticket_rpc = RpcProxy('ticket')
    chat_rpc = RpcProxy('chat')
    match_rpc = RpcProxy('match')
    player_rpc = RpcProxy('player')

    @http("GET", "/ticket")
    def get_ticket(self, request):
        return self.ticket_rpc.get_ticket("user")

    @http("POST", "/login")
    def login(self, request):
        schema = LoginSchema(strict=True)

        try:
            login_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        username = login_data["username"]
        password = login_data["password"]

        try:
            user_data = self.auth.login(username, password)
        except RemoteError:
            return 400, "Invalid Credentials"

        return str(user_data)

    @http("POST", "/signup")
    def signup(self, request):
        schema = LoginSchema(strict=True)

        try:
            login_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        username = login_data["username"]
        password = login_data["password"]

        if self.auth.signup(username, password):
            return 200, "Successful sign-up"
        else:
            return 500, "Couldn't sign-up"

    @srpc
    def subscribe_chat(self, socket_id):
        self.hub.subscribe(socket_id, 'chat')
        return 'subscribed to chat'

    @srpc
    def create_room(self, socket_id, sender, room_name):
        room_code = self.chat_rpc.create_room(room_name)
        self.hub.subscribe(socket_id, room_code)

    @srpc
    def subscribe_room(self, socket_id, room_code):
        self.hub.subscribe(socket_id, room_code)

    @srpc
    def unsubscribe_room(self, socket_id, room_code):
        self.hub.subscribe(socket_id, room_code)

    @srpc
    def process_message(self, socket_id, sender, content, room_code=None):
        if not self.chat_rpc.validate_message(sender, content):
            raise ValueError("Not valid message or sender")

        channel = 'chat' if room_code is None else room_code
        room_name = room_code.split(';')[1] if room_code else None

        self.hub.broadcast(channel, 'new_message', {
            "sender": sender,
            "content": content,
            "room": room_name
        })
