"""Flask app del ERP Livskin refactorizado."""
from flask import Flask

from config import settings
from routes.api_catalogo import bp as catalogo_bp
from routes.api_client_lookup import bp as client_lookup_bp
from routes.api_cliente import bp as cliente_bp
from routes.api_config import bp as config_bp
from routes.api_dashboard import bp as dashboard_bp
from routes.api_gasto import bp as gasto_bp
from routes.api_libro import bp as libro_bp
from routes.api_pagos import bp as pagos_bp
from routes.api_venta import bp as venta_bp
from routes.legacy_forms import bp as legacy_forms_bp
from routes.views import bp as views_bp


def create_app() -> Flask:
    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = settings.flask_secret_key

    flask_app.register_blueprint(views_bp)
    flask_app.register_blueprint(legacy_forms_bp)
    flask_app.register_blueprint(client_lookup_bp)
    flask_app.register_blueprint(cliente_bp)
    flask_app.register_blueprint(catalogo_bp)
    flask_app.register_blueprint(config_bp)
    flask_app.register_blueprint(dashboard_bp)
    flask_app.register_blueprint(gasto_bp)
    flask_app.register_blueprint(libro_bp)
    flask_app.register_blueprint(pagos_bp)
    flask_app.register_blueprint(venta_bp)

    @flask_app.route("/ping")
    def ping() -> str:
        return "pong"

    return flask_app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=settings.flask_env != "production")
