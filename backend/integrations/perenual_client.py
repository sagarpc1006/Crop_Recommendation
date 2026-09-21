"""External Plant API client scaffold (Perenual / Trefle).

Provides interface contract for fetching species and environmental requirements.
Actual API communication will be activated in future stages.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PerenualClient:
    """Client for communicating with the Perenual Plant API."""

    BASE_URL = "https://perenual.com/api"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def is_configured(self) -> bool:
        """Check if client has an API key configured."""
        return bool(self.api_key)

    def search_species(self, query: str, page: int = 1) -> dict[str, Any]:
        """Search plant species by keyword.
        
        Note: Foundation stub. API call logic will be implemented in future phase.
        """
        if not self.is_configured():
            logger.info("Perenual API key not set; integration disabled.")
            return {"data": [], "message": "API key not configured."}
        
        # Integration logic will be implemented in future phase
        return {"data": [], "page": page}
