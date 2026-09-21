"""Standardized REST API response formatters."""

from typing import Any
from flask import jsonify, Response


def api_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    status_code: int = 200,
    meta: dict | None = None
) -> tuple[Response, int]:
    """Return a uniform JSON success response.
    
    Args:
        data: Payload data (dict, list, primitive, etc.).
        message: Informational message.
        status_code: HTTP status code.
        meta: Optional metadata such as pagination or query metrics.
        
    Returns:
        Tuple of (Flask Response, status code).
    """
    payload = {
        "success": True,
        "message": message,
        "data": data,
    }
    if meta is not None:
        payload["meta"] = meta
        
    return jsonify(payload), status_code


def error_response(
    message: str = "An error occurred",
    status_code: int = 400,
    details: Any = None
) -> tuple[Response, int]:
    """Return a uniform JSON error response.
    
    Args:
        message: Error explanation.
        status_code: HTTP error code.
        details: Optional technical details or validation errors.
        
    Returns:
        Tuple of (Flask Response, status code).
    """
    payload = {
        "success": False,
        "message": message,
        "error": {
            "code": status_code,
            "details": details
        }
    }
    return jsonify(payload), status_code
