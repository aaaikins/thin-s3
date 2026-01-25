"""Pytest configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    # TODO: Create and return a test client
    pass


@pytest.fixture
def sample_file():
    """Sample file for testing"""
    # TODO: Return a sample file for testing
    pass
