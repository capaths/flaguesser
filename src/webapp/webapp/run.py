import os

from app import SocketApp

PROD = os.environ.get("ENV") == "prod"

if __name__ == "__main__":
    app = SocketApp(for_production=PROD)
    app.run(host='0.0.0.0', port=8080 if PROD else 8081)
