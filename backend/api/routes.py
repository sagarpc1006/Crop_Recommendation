"""REST API Blueprint defining health check, catalog, and recommendation endpoints."""

from flask import Blueprint, current_app, request
from backend.utils.response import api_response, error_response
from backend.database.connection import check_db_connection, get_session_factory
from backend.services.recommendation_service import RecommendationService
from backend.services.plant_service import PlantService
from backend.services.plant_api_service import PlantApiService

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Module-level singleton — PlantApiService is stateless beyond its in-process cache
_plant_api = PlantApiService()


# ---------------------------------------------------------------------------
# Health / Info
# ---------------------------------------------------------------------------

@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify backend API and PostgreSQL connectivity."""
    db_status = check_db_connection()
    api_cache = _plant_api.cache_info()
    status_data = {
        "service": "Plant Recommendation Backend API",
        "status": "online",
        "environment": current_app.config.get("FLASK_ENV", "development"),
        "database": db_status,
        "external_plant_api": api_cache,
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
            "plants_search": "/api/plants/search?q=<query>",
            "plant_detail": "/api/plants/<id>",
            "plant_enrich": "/api/plants/<id>/enrich",
            "recommendations_generate": "/api/recommendations/generate",
            "recommendations_user": "/api/recommendations/<user_id>",
            "recommendations_history": "/api/recommendations/history",
        },
        "supported_criteria": [
            "soil_type",
            "climate",
            "sunlight",
            "space"
        ],
        "external_api_available": _plant_api.is_available(),
    }
    return api_response(data=info, message="System information")


# ---------------------------------------------------------------------------
# Plants
# ---------------------------------------------------------------------------

@api_bp.route("/plants", methods=["GET"])
def list_plants():
    """Retrieve plant catalog from database.

    Query params:
      limit  (int)  Max records to return (default 20, max 100)
      offset (int)  Pagination offset (default 0)
    """
    try:
        limit  = max(1, min(100, int(request.args.get("limit",  20))))
        offset = max(0,          int(request.args.get("offset",  0)))
    except (ValueError, TypeError):
        limit, offset = 20, 0

    SessionFactory = get_session_factory()
    session = SessionFactory()
    try:
        service = PlantService(session)
        plants = service.get_all_plants(limit=limit, offset=offset)
        return api_response(
            data=plants,
            message="Plant catalog retrieved successfully.",
            meta={"total": len(plants), "limit": limit, "offset": offset}
        )
    finally:
        session.close()


@api_bp.route("/plants/search", methods=["GET"])
def search_plants():
    """Search plants by name, soil_type, climate, or sunlight.

    Query params:
      q      (str)  Search query (required)
      source (str)  "local" | "external" | "all" (default "all")
      page   (int)  Page number for external API results (default 1)
    """
    query = request.args.get("q", "").strip()
    if not query:
        return error_response(message="Query parameter 'q' is required.", status_code=400)

    source = request.args.get("source", "all").lower()
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (ValueError, TypeError):
        page = 1

    results = []

    # 1. Local database search
    if source in ("local", "all"):
        SessionFactory = get_session_factory()
        session = SessionFactory()
        try:
            service = PlantService(session)
            local_results = service.search_plants(query)
        finally:
            session.close()
        results.extend(local_results)

    # 2. External API search (falls back gracefully when unavailable)
    external_results: list = []
    if source in ("external", "all") and _plant_api.is_available():
        external_results = _plant_api.search_plants(query, page=page)
        results.extend(external_results)

    return api_response(
        data=results,
        message=f"Found {len(results)} plants matching '{query}'.",
        meta={
            "query": query,
            "source": source,
            "external_api_used": bool(external_results),
        }
    )


@api_bp.route("/plants/<int:plant_id>", methods=["GET"])
def get_plant(plant_id: int):
    """Retrieve a single plant record by ID, combining external plant API data when available."""
    SessionFactory = get_session_factory()
    session = SessionFactory()
    try:
        service = PlantService(session)
        plant = service.get_plant_by_id(plant_id)
        if plant is None:
            return error_response(
                message=f"Plant with id={plant_id} not found.",
                status_code=404
            )
    finally:
        session.close()

    # Automatically combine with external API data if available
    if _plant_api.is_available():
        plant = _plant_api.enrich_plant_record(plant)

    return api_response(
        data=plant,
        message="Plant retrieved and enriched successfully." if plant.get("external_enriched") else "Plant retrieved successfully."
    )


@api_bp.route("/plants/<int:plant_id>/enrich", methods=["GET"])
def enrich_plant(plant_id: int):
    """Enrich a local plant record with external API data.

    Fetches the local plant from PostgreSQL, then overlays external care
    and media data from Perenual. Falls back to the local record if the
    external API is unavailable.

    Returns the merged plant dict with 'external_enriched' flag.
    """
    SessionFactory = get_session_factory()
    session = SessionFactory()
    try:
        service = PlantService(session)
        plant = service.get_plant_by_id(plant_id)
        if plant is None:
            return error_response(
                message=f"Plant with id={plant_id} not found.",
                status_code=404
            )
    finally:
        session.close()

    enriched = _plant_api.enrich_plant_record(plant)
    message = (
        "Plant enriched with external data."
        if enriched.get("external_enriched")
        else "External API unavailable — local data returned."
    )
    return api_response(data=enriched, message=message)


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------

@api_bp.route("/recommendations/generate", methods=["POST"])
def generate_recommendations():
    """Generate transparent, scoring-based plant recommendations.

    Accepts JSON body::

        {
            "soil_type": "Loamy",
            "climate": "Tropical",
            "sunlight": "Partial Shade",
            "space": "Small",
            "limit": 5,
            "user_id": 1,
            "enrich": true
        }

    Set ``enrich: true`` to overlay external API media/care data on results.
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

    enrich = bool(payload.get("enrich", False))

    SessionFactory = get_session_factory()
    session = SessionFactory()
    try:
        service = RecommendationService(session)
        result = service.generate_recommendations(
            criteria_data=payload,
            limit=limit,
            user_id=user_id
        )

        # Optionally enrich each recommendation's plant data with external API
        if enrich and _plant_api.is_available():
            for rec in result.get("recommendations", []):
                plant_data = rec.get("plant") or rec
                enriched_plant = _plant_api.enrich_plant_record(plant_data)
                rec.update(enriched_plant)
                rec["plant"] = enriched_plant

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


@api_bp.route("/recommendations/<int:user_id>", methods=["GET"])
def get_user_recommendations(user_id: int):
    """Retrieve recommendation history for a specific user.

    Query params:
      limit  (int)  Max records to return (default 50, max 100)

    Returns list of recommendation records containing:
    - User details (id, name, email)
    - Plant details (id, name, scientific_name, image_url, characteristics)
    - Recommendation date/time
    - Compatibility score (percentage and float)
    - User preference information (soil, climate, sunlight, space)
    """
    try:
        limit = max(1, min(100, int(request.args.get("limit", 50))))
    except (ValueError, TypeError):
        limit = 50

    SessionFactory = get_session_factory()
    session = SessionFactory()
    try:
        service = RecommendationService(session)
        history = service.get_user_recommendations(user_id=user_id, limit=limit)
        return api_response(
            data=history,
            message=f"Found {len(history)} recommendation records for user {user_id}.",
            status_code=200
        )
    finally:
        session.close()


@api_bp.route("/recommendations/history", methods=["GET"])
def get_recent_recommendation_history():
    """Retrieve recent recommendation history across users or sessions.

    Query params:
      limit   (int)  Max records to return (default 50, max 100)
      user_id (int)  Optional user ID filter
    """
    try:
        limit = max(1, min(100, int(request.args.get("limit", 50))))
    except (ValueError, TypeError):
        limit = 50

    user_id_param = request.args.get("user_id")
    user_id = None
    if user_id_param is not None:
        try:
            user_id = int(user_id_param)
        except (ValueError, TypeError):
            user_id = None

    SessionFactory = get_session_factory()
    session = SessionFactory()
    try:
        service = RecommendationService(session)
        if user_id is not None:
            history = service.get_user_recommendations(user_id=user_id, limit=limit)
        else:
            history = service.get_all_recommendations(limit=limit)
        return api_response(
            data=history,
            message=f"Found {len(history)} recent recommendation history records.",
            status_code=200
        )
    finally:
        session.close()

