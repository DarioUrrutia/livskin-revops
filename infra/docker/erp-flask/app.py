"""Flask app del ERP Livskin refactorizado.

Esqueleto inicial — routes, services, middleware se agregan en sesiones siguientes.
"""
from flask import Flask

from config import settings


def create_app() -> Flask:
    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = settings.flask_secret_key

    @flask_app.route("/ping")
    def ping() -> str:
        return "pong"

    return flask_app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=settings.flask_env != "production")
