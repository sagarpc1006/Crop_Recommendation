"""REST API Blueprint defining health check and foundational route skeletons."""

from flask import Blueprint, current_app, request
from backend.utils.response import api_response, error_response
from backend.database.connection import check_db_connection

api_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify backend API and PostgreSQL connectivity.
    
    Returns:
        JSON response with service status and database connectivity details.
    """
    db_status = check_db_connection()
    status_data = {
        "service": "Plant Recommendation Backend API",
        "status": "online",
        "environment": current_app.config.get("FLASK_ENV", "development"),
        "database": db_status,
    }
    
    # 200 if API is healthy; if DB is offline we still report API health with DB warning
    return api_response(
        data=status_data,
        message="Service health report",
        status_code=200
    )


@api_bp.route("/info", methods=["GET"])
def system_info():
    """Returns metadata about available system capabilities and architecture."""
    info = {
        "version": "1.0.0",
        "name": "Plant Recommendation Engine API",
        "endpoints": {
            "health": "/api/v1/health",
            "info": "/api/v1/info",
            "plants": "/api/v1/plants (stub)",
            "recommendations": "/api/v1/recommendations (stub)"
        },
        "supported_criteria": [
            "soil_type",
            "climate",
            "sunlight",
            "space_requirement"
        ]
    }
    return api_response(data=info, message="System information")


@api_bp.route("/plants", methods=["GET"])
def list_plants():
    """Skeleton endpoint for retrieving plant catalog (to be implemented in future phase)."""
    return api_response(
        data=[],
        message="Plant catalog endpoint ready for data integration in upcoming stage.",
        meta={"total": 0}
    )


@api_bp.route("/recommendations", methods=["POST"])
def get_recommendations():
    """Skeleton endpoint for plant recommendations (to be implemented in future phase)."""
    payload = request.get_json(silent=True) or {}
    return api_response(
        data={
            "received_input": payload,
            "recommendations": []
        },
        message="Recommendation logic endpoint ready for algorithm implementation in upcoming stage."
    )
