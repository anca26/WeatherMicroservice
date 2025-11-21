import mongomock
from datetime import datetime, timezone, timedelta
import ui.app as ui

def _seed(coll):
    now = datetime.now(timezone.utc)
    coll.insert_one({
        "city": "Iasi",
        "temperature_c": 9.7,
        "description": "clear",
        "humidity": 42,
        "wind_speed_ms": 3.1,
        "timestamp": now - timedelta(hours=2),
    })
    coll.insert_one({
        "city": "Iasi",
        "temperature_c": 10.1,
        "description": "clear",
        "humidity": 40,
        "wind_speed_ms": 3.0,
        "timestamp": now - timedelta(hours=1),
    })

def test_index_renders_with_points(monkeypatch):
    mock_client = mongomock.MongoClient()
    coll = mock_client["weather_db"]["weather_data"]
    _seed(coll)
    monkeypatch.setattr(ui, "coll", coll)

    app = ui.app
    with app.test_client() as c:
        r = c.get("/?city=Iasi&range=1d")
        assert r.status_code == 200
        assert b"Temperature" in r.data
        assert b"<canvas" in r.data

def test_fetch_post_redirect(monkeypatch):
    monkeypatch.setattr(ui, "fetch_data", lambda city: (object(), None))
    mock_client = mongomock.MongoClient()
    monkeypatch.setattr(ui, "coll", mock_client["weather_db"]["weather_data"])

    app = ui.app
    with app.test_client() as c:
        r = c.post("/fetch", data={"city":"Iasi","range":"1d"})
        assert r.status_code in (302, 303)
