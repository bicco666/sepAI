import asyncio
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.store import ideas_store
from src.models import IdeaStatus

client = TestClient(app)


def test_create_and_transition_idea():
    # ensure fresh store
    ideas_store.clear()

    payload = {
        "source": "research",
        "asset": "SOL",
        "type": "yield",
        "risk": 2,
        "budget": 0.5,
        "ttl": 3600,
    }
    r = client.post("/api/v1/ideas", json=payload)
    assert r.status_code == 200
    idea = r.json()
    assert idea["source"] == "research"
    assert idea["status"] == IdeaStatus.NEW

    idea_id = idea["id"]

    # valid transition: review
    r = client.post(f"/api/v1/ideas/{idea_id}/review")
    assert r.status_code == 200
    assert r.json()["status"] == IdeaStatus.NEEDS_REVIEW

    # invalid transition: schedule directly from NEEDS_REVIEW -> should be 400
    r = client.post(f"/api/v1/ideas/{idea_id}/schedule")
    assert r.status_code == 400

    # move to READY_FOR_QA then APPROVED then SCHEDULED
    r = client.post(f"/api/v1/ideas/{idea_id}/qa-ready")
    assert r.status_code == 200
    r = client.post(f"/api/v1/ideas/{idea_id}/approve")
    assert r.status_code == 200
    r = client.post(f"/api/v1/ideas/{idea_id}/schedule")
    assert r.status_code == 200
    assert r.json()["status"] == IdeaStatus.SCHEDULED


def test_not_found_transitions():
    # not existing id
    r = client.post("/api/v1/ideas/nonexistent/review")
    assert r.status_code == 404
