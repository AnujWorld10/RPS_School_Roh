from sqlalchemy.exc import OperationalError


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == {"status": "ready", "database": True}


def test_readiness_returns_503_when_database_is_unavailable(client, monkeypatch):
    from app import main

    monkeypatch.setattr(main, "check_database_connection", lambda: False)

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["success"] is False
    assert response.json()["errors"][0]["code"] == "DATABASE_UNAVAILABLE"


def test_readiness_returns_503_when_database_probe_raises(client, monkeypatch):
    from app import main

    def fail_probe():
        raise OperationalError("SELECT 1", {}, RuntimeError("database unavailable"))

    monkeypatch.setattr(main, "check_database_connection", fail_probe)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["errors"][0]["code"] == "DATABASE_UNAVAILABLE"


def test_liveness_does_not_depend_on_database(client, monkeypatch):
    from app import main

    def fail_probe():
        raise OperationalError("SELECT 1", {}, RuntimeError())

    monkeypatch.setattr(main, "check_database_connection", fail_probe)

    response = client.get("/live")

    assert response.status_code == 200
    assert response.json()["data"] == {"status": "alive"}
