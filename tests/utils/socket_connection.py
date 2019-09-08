import json
import warnings

from websocket import create_connection, WebSocketTimeoutException


class SocketConnection:
    unseen_messages = dict()

    def __init__(self, url):
        self.ws = create_connection(url)

        # consume connection event
        self.ws.recv()

    def save_message(self, message: dict):
        if self.unseen_messages.get(message["type"]) is None:
            self.unseen_messages[message["type"]] = list()
        self.unseen_messages[message["type"]].insert(0, message)

    def update_message_list(self, timeout: float = 0.7):
        self.ws.settimeout(timeout)
        try:
            while True:
                message = json.loads(self.ws.recv())
                self.save_message(message)
        except WebSocketTimeoutException:
            return

    def send(self, method: str, data: dict = None, timeout: float = 0.7):
        if data is None:
            data = dict()

        payload = {
            'method': method,
            'data': data
        }
        self.ws.send(json.dumps(payload))

        responses = self.recv("result", timeout)
        if len(responses) > 1:
            warnings.warn(f"received {len(responses)} results. Ignoring {len(responses)-1} messages")
        elif len(responses) == 0:
            warnings.warn("No results")
            return
        return responses[-1]

    def recv(self, s_type: str, timeout: float = 0.7):
        self.update_message_list(timeout)
        messages = self.unseen_messages.get(s_type)
        if messages is not None:
            self.unseen_messages[s_type] = list()
            return messages
        return list()

    def close(self):
        self.ws.close()

