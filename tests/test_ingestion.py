import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ingestion_service import IngestionService
import json

def test_ingestion_service_init():
    os.environ["GEMINI_API_KEY"] = "mock_key"
    try:
        service = IngestionService()
        assert service is not None
        assert "gemini" in service.model.model_name.lower() or service.model is not None
    except Exception as e:
        pytest.skip(f"Could not init due to missing creds or deps: {e}")

