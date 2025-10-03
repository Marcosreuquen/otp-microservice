from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from contextlib import contextmanager

from app.main import app

client = TestClient(app)


def test_health_all_ok(monkeypatch):
    # Mock redis_client.ping to return True
    with patch("app.routes.healthRouter.redis_client") as mock_redis:
        mock_redis.ping = AsyncMock(return_value=True)

        # Mock DB session exec to succeed using a simple contextmanager
        with patch("app.routes.healthRouter.db") as mock_db:
            @contextmanager
            def healthy_session():
                class Sess:
                    def exec(self, q):
                        return None
                yield Sess()

            mock_db.session = healthy_session

            r = client.get("/health/")
            assert r.status_code == 200
            j = r.json()
            assert j.get("ok") is True
            assert "redis" in j["services"]
            assert "db" in j["services"]


def test_health_db_down(monkeypatch):
    # Redis OK, DB fails
    with patch("app.routes.healthRouter.redis_client") as mock_redis:
        mock_redis.ping = AsyncMock(return_value=True)

        with patch("app.routes.healthRouter.db") as mock_db:
            @contextmanager
            def failing_session():
                raise Exception("db down")
                yield  # pragma: no cover

            mock_db.session = failing_session

            r = client.get("/health/")
            assert r.status_code == 503
            j = r.json()
            assert j.get("ok") is False
            assert j["services"]["db"]["ok"] is False
