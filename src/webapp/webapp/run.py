import os

from app import SocketApp

PROD = os.environ.get("ENV") == "prod"
PORT = os.environ.get("PORT", 8080)

if __name__ == "__main__":
    app = SocketApp(for_production=PROD)
    app.run(host='0.0.0.0', port=PORT if PROD else 8081)
