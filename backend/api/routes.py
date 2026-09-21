"""REST API Blueprint defining health check, catalog, and recommendation endpoints."""

from flask import Blueprint, current_app, request
from backend.utils.response import api_response, error_response
from backend.database.connection import check_db_connection, get_session_factory
from backend.services.recommendation_service import RecommendationService
from backend.services.plant_service import PlantService

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify backend API and PostgreSQL connectivity."""
    db_status = check_db_connection()
    status_data = {
        "service": "Plant Recommendation Backend API",
        "status": "online",
        "environment": current_app.config.get("FLASK_ENV", "development"),
        "database": db_status,
    }
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
            "health": "/api/health",
            "info": "/api/info",
            "plants": "/api/plants",
            "recommendations_generate": "/api/recommendations/generate",
        },
        "supported_criteria": [
            "soil_type",
            "climate",
            "sunlight",
            "space"
        ]
    }
    return api_response(data=info, message="System information")


@api_bp.route("/plants", methods=["GET"])
def list_plants():
    """Retrieve plant catalog from database or default catalog."""
    SessionFactory = get_session_factory()
    session = SessionFactory()
    try:
        service = PlantService(session)
        plants = service.get_all_plants()
        return api_response(
            data=plants,
            message="Plant catalog retrieved successfully.",
            meta={"total": len(plants)}
        )
    finally:
        session.close()


@api_bp.route("/recommendations/generate", methods=["POST"])
def generate_recommendations():
    """Generate transparent, scoring-based plant recommendations.
    
    Accepts JSON body:
    {
        "soil_type": "Loamy",
        "climate": "Tropical",
        "sunlight": "Partial Shade",
        "space": "Small",
        "limit": 5,
        "user_id": 1  (optional)
    }
    """
    if not request.is_json and request.content_length and request.content_length > 0:
        return error_response(
            message="Request content-type must be application/json",
            status_code=400
        )

    payload = request.get_json(silent=True) or {}
    limit = payload.get("limit", 5)
    try:
        limit = max(1, min(50, int(limit)))
    except (ValueError, TypeError):
        limit = 5

    user_id = payload.get("user_id")
    if user_id is not None:
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            user_id = None

    SessionFactory = get_session_factory()
    session = SessionFactory()
    try:
        service = RecommendationService(session)
        result = service.generate_recommendations(
            criteria_data=payload,
            limit=limit,
            user_id=user_id
        )
        return api_response(
            data=result,
            message=f"Generated {len(result['recommendations'])} plant recommendations.",
            status_code=200
        )
    except Exception as e:
        return error_response(
            message=f"Failed to compute recommendations: {str(e)}",
            status_code=500
        )
    finally:
        session.close()


@api_bp.route("/recommendations", methods=["POST"])
def legacy_recommendations():
    """Legacy recommendation endpoint alias forwarding to recommendation generator."""
    return generate_recommendations()
