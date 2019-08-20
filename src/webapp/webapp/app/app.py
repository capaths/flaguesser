import os

from flask import Flask
from flask_socketio import SocketIO
from flask_webpack_loader import WebpackLoader


import re
from .router import route_app
from .socket import prepare_sockets

PROD = os.environ.get("ENV") == "prod"


class SocketApp:

    def __init__(self, for_production: bool = False):
        template_folder = "../dist" if for_production else "./templates"
        static_folder = "../dist/static" if for_production else "static"

        self.app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
        route_app(self.app, for_production=for_production)

        self.socketio = SocketIO(self.app)
        prepare_sockets(self.socketio)

        if not for_production:
            WEBPACK_LOADER = {
                'BUNDLE_DIR_NAME': os.path.join('static', 'bundles'),
                'STATIC_URL': 'static',
                'STATS_FILE': './frontend/webpack-stats.json',
                'POLL_INTERVAL': 0.1,
                'TIMEOUT': None,
                'IGNORES': [re.compile(r'.+\.hot-update.js'), re.compile(r'.+\.map')],
                'CACHE': False
            }

            webpack_loader = WebpackLoader(self.app)
            webpack_loader.config = WEBPACK_LOADER

    def run(self, host='0.0.0.0', port=8080):
        self.socketio.run(self.app, host=host, port=port, debug=True)
