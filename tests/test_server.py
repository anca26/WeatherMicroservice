import types
import pytest
import server.server as srv
from generated import weather_pb2

class DummyCtx:
    def __init__(self): self.code=None; self.details=None
    def set_code(self, c): self.code = c
    def set_details(self, d): self.details = d
    def abort(self, code, details): raise RuntimeError(f"aborted {code} {details}")

def test_getweather_success(monkeypatch):
    class FakeResp:
        status_code = 200
        def raise_for_status(self): pass
        def json(self):
            return {
                "name": "Iasi",
                "main": {"temp": 11.2, "humidity": 50},
                "weather": [{"description": "few clouds"}],
                "wind": {"speed": 3.8},
            }
    monkeypatch.setattr(srv, "requests", types.SimpleNamespace(get=lambda *a, **k: FakeResp()))

    
    saved = {}
    def fake_save(**kwargs): saved.update(kwargs)
    srv.repo.save_weather_data = lambda **kw: fake_save(**kw)

    svc = srv.WeatherService()
    ctx = DummyCtx()
    resp = svc.GetWeather(weather_pb2.WeatherRequest(city="Iasi"), ctx)

    assert not resp.error
    assert resp.city == "Iasi"
    assert resp.temperature_c == pytest.approx(11.2)
    assert resp.humidity == 50
    assert resp.description == "few clouds"
    assert resp.wind_speed_ms == pytest.approx(3.8)

    assert saved["city"] == "Iasi"
    assert saved["temperature_c"] == 11.2

def test_getweather_empty_city():
    svc = srv.WeatherService()
    ctx = DummyCtx()
    resp = svc.GetWeather(weather_pb2.WeatherRequest(city="  "), ctx)
    assert "empty" in resp.error.lower()
