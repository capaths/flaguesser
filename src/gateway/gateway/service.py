
""" Gateway """
import os
import json
import time

import requests

from nameko.timer import timer
from nameko.rpc import RpcProxy
from nameko.exceptions import BadRequest
from nameko.extensions import DependencyProvider

from nameko.web.websocket import rpc as srpc

from marshmallow import ValidationError

from gateway.sockets import WebSocketHubProviderExt
from gateway.schemas import LoginSchema, SignUpSchema, TicketSchema
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

    auth = RpcProxy('access')

    ticket_rpc = RpcProxy('ticket')
    chat_rpc = RpcProxy('chat')
    match_rpc = RpcProxy('match')
    player_rpc = RpcProxy('player')

    @cors_http("GET", "/ticket/get/<int:id>")
    def get_ticket(self, request, id):
        ticket_url = os.getenv("TICKET_URL", "http://localhost:9000/")
        return requests.get(ticket_url + f"/get/{id}")

    @cors_http("GET", "/ticket/all")
    def get_all_tickets(self, request):
        ticket_url = os.getenv("TICKET_URL", "http://localhost:9000/")
        return requests.get(ticket_url + "/all")

    @cors_http("GET", "/match/all")
    def get_all_matches(self, request):
        return json.dumps(self.match_rpc.get_all_matches())

    @cors_http("GET", "/match/byplayer/<string:username>")
    def get_match_by_player(self, request, username):
        return json.dumps(self.match_rpc.get_player_matches(username))

    @cors_http("POST", "/ticket/save")
    def get_all_tickets(self, request):
        schema = TicketSchema(strict=True)

        try:
            ticket_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            return 400, f"Not valid JSON: {exc}"
        except ValidationError as exc:
            return 400, f"Not valid arguments: {exc}"

        ticket_url = os.getenv("TICKET_URL", "http://localhost:9000/")
        return requests.post(ticket_url + "/save", json={
            "title": ticket_data["title"],
            "description": ticket_data["description"]
        }).json()

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
        schema = SignUpSchema(strict=True)

        try:
            signup_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        username = signup_data["username"]
        password = signup_data["password"]
        country = signup_data["country"]

        if self.auth.signup(username, password, country):
            user_data = self.auth.login(username, password)
            if user_data:
                return 200, user_data
            return 500, "Something went wrong"
        else:
            return 500, "User already exists"

    def try_socket_id(self, socket_id, username):
        if self.hub.is_identified(socket_id):
            return
        if username is not None:
            self.hub.identify_socket(socket_id, username)
            if not self.hub.is_identified(socket_id):
                raise PermissionError("Couldn't identify socket")
            return
        raise PermissionError("Not identified connection")

    @srpc
    def identify(self, socket_id, username):
        self.try_socket_id(socket_id, username)

    @srpc
    def subscribe_chat(self, socket_id, username=None):
        self.try_socket_id(socket_id, username)
        self.hub.subscribe(socket_id, 'chat')

    @srpc
    def subscribe_challenge(self, socket_id, username=None):
        self.try_socket_id(socket_id, username)
        if not self.hub.is_identified(socket_id):
            self.hub.subscribe(socket_id, 'challenge')
            return True
        return False

    # Chat
    @srpc
    def create_room(self, socket_id, room_name, username=None):
        self.try_socket_id(socket_id, username)
        username = self.hub.get_username(socket_id)
        if username is None:
            raise PermissionError("Not identified connection")

        room_code = self.chat_rpc.create_room(room_name, username)
        if room_code is None:
            raise ValueError(f"Player {username} does not exist")

        room = json.loads(room_code)
        self.hub.register_room(room["room"]["code"])
        self.hub.unicast(socket_id, 'room_data', room)

    @srpc
    def subscribe_room(self, socket_id, room_code, username=None):
        self.try_socket_id(socket_id, username)
        self.hub.subscribe_room(socket_id, room_code)

    @srpc
    def unsubscribe_room(self, socket_id, room_code, username=None):
        self.try_socket_id(socket_id, username)
        self.hub.unsubscribe(socket_id, room_code)

    @srpc
    def process_message(self, socket_id, content, room_code=None, username=None):
        self.try_socket_id(socket_id, username)
        username = self.hub.get_username(socket_id)
        if username is None:
            raise PermissionError("Not identified connection")

        if not self.chat_rpc.validate_message(username, content):
            raise ValueError("Not valid message")

        if room_code is not None and not self.hub.is_valid_room(room_code):
            raise ValueError("Not a valid room")

        channel = 'chat' if room_code is None else f"chat;{room_code}"

        self.hub.broadcast(channel, 'new_message', {
            "sender": username,
            "content": content,
            "room_code": room_code,
        })

    # Match

    @cors_http("GET", "/player/<string:username>")
    def get_player(self, request, username):
        return json.dumps(self.player_rpc.get_player_by_username(username))

    @cors_http("GET", "/online_users")
    def get_connected_users(self, request):
        usernames = self.hub.get_active_users()
        users = {}
        for username in usernames:
            player = self.player_rpc.get_player_by_username(username)
            users[username] = player
        return json.dumps(users)

    @srpc
    def challenge(self, socket_id, challenged, username=None):
        self.try_socket_id(socket_id, username)
        username = self.hub.get_username(socket_id)
        if username is None:
            raise PermissionError("Not identified connection")

        start_time = time.time()
        code = self.match_rpc.generate_match_code(username, challenged, start_time)
        self.hub.unicast(self.hub.get_socket_id(challenged), 'challenge', {
            "sender": username,
            "start_time": start_time,
            "code": code
        })

    @srpc
    def accept_challenge(self, socket_id: str, challenger: str, start_time: float, code: str, username=None):
        self.try_socket_id(socket_id, username)

        challenged = self.hub.get_username(socket_id)
        if challenged is None:
            raise PermissionError("Not identified connection")

        real_code = self.match_rpc.generate_match_code(challenger, challenged, start_time)
        if code != real_code:
            raise ValueError(f"Invalid challenge code")

        socket_id_b = self.hub.get_socket_id(challenger)
        if socket_id_b is None:
            raise ValueError("Challenger doesn't exist")

        match_channel = f"match;{code}"
        self.hub.subscribe(socket_id, match_channel)
        self.hub.subscribe(socket_id_b, match_channel)

        self.hub.begin_match(code, socket_id, socket_id_b)

        end_time = self.hub.get_match(socket_id)["end_time"]
        self.hub.broadcast(match_channel, "match_begins", {
            "code": code,
            "flags": self.match_rpc.get_flags_images(code),
            "end_time": end_time
        })

    @srpc
    def guess_flag(self, socket_id, guess, username=None):
        self.try_socket_id(socket_id, username)

        match = self.hub.get_match(socket_id)
        code = match["code"]

        flag_url = self.match_rpc.guess_flag(code, guess)
        not_guessed_yet = self.hub.guess_flag(socket_id, flag_url)
        if not_guessed_yet:
            flag_url = self.match_rpc.guess_flag(code, guess)

        # broadcast guess result
        match_channel = f"match;{code}"
        self.hub.broadcast(match_channel, "guess", {
            "guesser": self.hub.get_username(socket_id),
            "guess": guess,
            "url": flag_url,
        })

        # end match if someone reached maximum score
        updated_match = self.hub.get_match(socket_id)
        if updated_match["player1"]["score"] >= 20 or updated_match["player2"]["score"] >= 20:
            self.hub.end_match(code)

    def end_match(self, code):
        match = self.hub.pop_match(code)
        if match is None:
            raise ValueError(f"Can't end unregistered match: {code}")

        player1 = match["player1"]
        player2 = match["player2"]

        username1 = self.hub.get_username(player1["socket_id"])
        username2 = self.hub.get_username(player2["socket_id"])

        score1 = player1["score"]
        score2 = player2["score"]

        match_channel = f"match;{code}"
        self.hub.broadcast(match_channel, "end_match", {
            "username1": username1,
            "username2": username2,
            "score1": score1,
            "score2": score2
        })

        self.match_rpc.end_match(username1, username2, score1, score2)
        if score1 != score2:
            winner = username1 if score1 > score2 else username2
            loser = username1 if score1 < score2 else username2

            self.player_rpc.update_elo(winner, 10)
            self.player_rpc.update_elo(loser, -10)

        self.hub.unsubscribe(player1["socket_id"], match_channel)
        self.hub.unsubscribe(player2["socket_id"], match_channel)

    @timer(interval=0.5)
    def update_timer(self):
        for match in self.hub.get_timed_out_matches():
            self.end_match(match["code"])

