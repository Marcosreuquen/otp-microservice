from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.utils.exceptionHandler import fastapi_exception_handler, ApiException
from app.utils.errors import NotFound


def create_app():
    app = FastAPI()

    # register handler
    app.add_exception_handler(ApiException, fastapi_exception_handler)

    @app.get("/raise_not_found")
    def raise_not_found():
        raise NotFound("Resource missing")

    return app


def test_api_exception_handler_returns_structured_json():
    app = create_app()
    client = TestClient(app)

    resp = client.get("/raise_not_found")
    assert resp.status_code == 404
    j = resp.json()
    assert j.get("error") is True
    assert "Resource missing" in j.get("message")
