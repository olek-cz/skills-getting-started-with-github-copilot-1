import copy
import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

app_path = Path(__file__).resolve().parents[1] / "src" / "app.py"
spec = importlib.util.spec_from_file_location("app_module", app_path)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)


@pytest.fixture(autouse=True)
def restore_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))


client = TestClient(app_module.app)


def test_unregister_participant_removes_student_from_activity():
    response = client.delete(
        "/activities/Chess Club/participants?email=michael@mergington.edu"
    )

    assert response.status_code == 200
    assert "Unregistered michael@mergington.edu" in response.json()["message"]
    assert "michael@mergington.edu" not in app_module.activities["Chess Club"]["participants"]


def test_unregister_participant_returns_not_found_for_unknown_student():
    response = client.delete(
        "/activities/Chess Club/participants?email=missing@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
