"""Flask Application Entry Point and Factory.

Constructs and configures the Flask application, sets up CORS,
registers REST blueprints, and handles database lifecycle.
"""

import os
from flask import Flask, request, jsonify
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

    @app.route("/")
    def index():
        if "text/html" in request.headers.get("Accept", ""):
            return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FloraMatch Backend API</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; display: flex; justify-content: center; align-items: center; min-height: 80vh; margin: 0; }
  .card { background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 36px; max-width: 620px; width: 100%; box-shadow: 0 15px 35px rgba(0,0,0,0.5); }
  h1 { color: #10b981; margin-top: 0; display: flex; align-items: center; gap: 10px; font-size: 26px; }
  .badge { display: inline-block; background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); padding: 5px 12px; border-radius: 9999px; font-size: 13px; font-weight: 600; margin-bottom: 20px; }
  p { color: #94a3b8; line-height: 1.6; font-size: 15px; }
  ul { list-style: none; padding: 0; margin: 24px 0; }
  li { margin: 14px 0; background: #0f172a; padding: 12px 16px; border-radius: 8px; border: 1px solid #334155; }
  a { color: #38bdf8; text-decoration: none; font-weight: 500; }
  a:hover { text-decoration: underline; }
  .btn { display: inline-block; background: #10b981; color: #ffffff; padding: 12px 22px; border-radius: 8px; font-weight: 600; text-decoration: none; margin-top: 15px; font-size: 15px; }
  .btn:hover { background: #059669; }
</style>
</head>
<body>
<div class="card">
  <div class="badge">● Backend Status: Online</div>
  <h1>🌿 FloraMatch Backend API</h1>
  <p>The Flask REST API backend server is operational and connected to the database.</p>
  <ul>
    <li>🌐 <strong>Web Application (Streamlit):</strong> <a href="http://localhost:8501" target="_blank">http://localhost:8501</a></li>
    <li>🩺 <strong>Health Check:</strong> <a href="/api/health">/api/health</a></li>
    <li>📋 <strong>System Information:</strong> <a href="/api/info">/api/info</a></li>
    <li>🌱 <strong>Plant Catalog:</strong> <a href="/api/plants">/api/plants</a></li>
  </ul>
  <a href="http://localhost:8501" class="btn" target="_blank">Open FloraMatch Web Application →</a>
</div>
</body>
</html>"""
        return jsonify({
            "status": "online",
            "service": "FloraMatch Plant Recommendation Backend API",
            "health": "/api/health",
            "info": "/api/info",
            "frontend_ui": "http://localhost:8501"
        })

    return app


# Module-level instance for WSGI servers (Gunicorn / Railway / Render)
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("FLASK_RUN_PORT", 5000))
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    debug = app.config.get("DEBUG", True)
    
    print(f" * Starting Plant Recommendation Backend on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, use_reloader=False)
