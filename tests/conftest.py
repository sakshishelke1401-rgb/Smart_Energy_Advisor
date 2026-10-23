import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app import create_app  # noqa: E402


class Client:
    """Test client that carries the CSRF token like the browser does."""

    def __init__(self, app):
        self.c = app.test_client()
        self.csrf = ""
        self.refresh()

    def refresh(self):
        self.csrf = self.c.get("/api/me").get_json()["csrf"]

    def get(self, path, **kw):
        return self.c.get(path, **kw)

    def post(self, path, json=None, **kw):
        r = self.c.post(path, json=json, headers={"X-CSRF-Token": self.csrf}, **kw)
        data = r.get_json(silent=True) or {}
        if data.get("csrf"):
            self.csrf = data["csrf"]
        return r


@pytest.fixture()
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})


@pytest.fixture()
def client(app):
    return Client(app)


@pytest.fixture()
def guest(client):
    assert client.post("/api/guest").status_code == 200
    return client
