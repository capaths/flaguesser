import requests
from flask import request, render_template

from sys import stdout


def route_app(app, for_production: bool = False):
    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route('/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        country = data["country"]

        if for_production:
            req = requests.post("http://gateway:8000/signup", json={
                "username": username,
                "password": password,
                "country": country
            })

            if req.status_code != 200:
                return req.content.decode(), req.status_code
            app.logger.info('new user: %s', username)
        return login()

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data["username"]
        password = data["password"]

        if not for_production:
            user = {
                "jwt": "test-jwt",
                "user": {
                    "username": "testUser",
                    "country": "Chile"
                }
            }
            status_code = 200
        else:
            req = requests.post("http://gateway:8000/login", json={
                "username": username,
                "password": password
            })
            user = req.content.decode()
            status_code = req.status_code

        return user, status_code

    @app.route('/logout', methods=['POST'])
    def logout():
        data = request.get_json()
        jwt = data["jwt"]

        if for_production:
            req = requests.post("http://gateway:8000/logout", json={
                "jwt": jwt,
            })

        return "", 200
