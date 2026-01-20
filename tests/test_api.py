import os
import pytest


def test_root_and_health_endpoints(monkeypatch):
    # prevent real DB connection by pointing to an in-memory SQLite database
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("message")

    r2 = client.get("/health")
    assert r2.status_code == 200
    assert r2.json() == {"status": "healthy"}
