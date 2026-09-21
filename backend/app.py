"""Flask Application Entry Point and Factory.

Constructs and configures the Flask application, sets up CORS,
registers REST blueprints, and handles database lifecycle.
"""

import os
from flask import Flask
from flask_cors import CORS
from backend.config import get_config, BaseConfig
from backend.api.routes import api_bp
from backend.database.connection import init_db


def create_app(config_class: type[BaseConfig] | None = None) -> Flask:
    """Application Factory to initialize and configure the Flask app."""
    if config_class is None:
        config_class = get_config()

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure CORS for Streamlit frontend and local dev
    CORS(
        app,
        resources={r"/api/*": {"origins": config_class.CORS_ORIGINS}},
        supports_credentials=True
    )

    # Register API Blueprints under /api and alias /api/v1
    app.register_blueprint(api_bp)
    app.register_blueprint(api_bp, url_prefix="/api/v1", name="api_v1")

    # Initialize database tables if PostgreSQL is accessible
    with app.app_context():
        init_db()

    return app


# Module-level instance for WSGI servers (Gunicorn / Railway / Render)
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("FLASK_RUN_PORT", 5000))
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    debug = app.config.get("DEBUG", True)
    
    print(f" * Starting Plant Recommendation Backend on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
