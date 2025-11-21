from freezegun import freeze_time
import mongomock
import server.repository as repo_mod

@freeze_time("2025-11-20 12:00:00+00:00")
def test_save_and_query_observation(monkeypatch):
    monkeypatch.setattr(repo_mod, "MongoClient", mongomock.MongoClient)

    repo = repo_mod.WeatherRepository(
        uri="mongodb://ignored:27017", db="weather_db", collection="weather_data"
    )

    repo.save_weather_data("Iasi", 10.5, "clear", 45, 3.2)
    docs = repo.get_recent_weather_data("Iasi", limit=5)

    assert len(docs) == 1
    d = docs[0]
    assert d["city"] == "Iasi"
    assert d["temperature_c"] == 10.5
    assert d["humidity"] == 45
    assert d["description"] == "clear"
    assert d["wind_speed_ms"] == 3.2
    assert "timestamp" in d  
