from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.main import app, create_store
from app.store import CityNotFoundError


class FakeStore:
    def __init__(self) -> None:
        self.records: dict[str, dict[str, object]] = {}

    def health(self) -> bool:
        return True

    def upsert_city(self, city: str, population: int) -> dict[str, object]:
        record = {
            "city": city.strip(),
            "population": population,
            "status": "created",
            "updated_at": datetime.now(UTC).isoformat(),
        }
        self.records[city.strip().lower()] = record
        return record

    def get_city(self, city: str) -> dict[str, object]:
        key = city.strip().lower()
        if key not in self.records:
            raise CityNotFoundError(city)
        return {**self.records[key], "status": "ok"}

    def seed_default_cities(self, records: list[dict[str, object]]) -> int:
        created = 0
        for record in records:
            key = str(record["city"]).strip().lower()
            if key in self.records:
                continue
            self.records[key] = {
                **record,
                "status": "created",
                "updated_at": datetime.now(UTC).isoformat(),
            }
            created += 1
        return created

    def list_cities(self, size: int = 25) -> list[dict[str, object]]:
        return list(self.records.values())[:size]


def make_client() -> tuple[TestClient, FakeStore]:
    store = FakeStore()
    app.dependency_overrides[create_store] = lambda: store
    return TestClient(app), store


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_healthz_returns_ok() -> None:
    client, _ = make_client()
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.text == "OK"


def test_upsert_and_query_city() -> None:
    client, _ = make_client()
    upsert = client.put("/cities/Dubai", json={"population": 3331420})
    assert upsert.status_code == 200
    assert upsert.json()["city"] == "Dubai"
    assert upsert.json()["population"] == 3331420

    query = client.get("/cities/Dubai")
    assert query.status_code == 200
    assert query.json()["population"] == 3331420


def test_upsert_updates_existing_city() -> None:
    client, _ = make_client()
    assert client.put("/cities/Dubai", json={"population": 10}).status_code == 200
    response = client.put("/cities/Dubai", json={"population": 20})
    assert response.status_code == 200
    assert response.json()["population"] == 20


def test_unknown_city_returns_404() -> None:
    client, _ = make_client()
    response = client.get("/cities/Atlantis")
    assert response.status_code == 404
    assert response.json()["detail"] == "City not found"


def test_invalid_population_returns_422() -> None:
    client, _ = make_client()
    response = client.put("/cities/Dubai", json={"population": -1})
    assert response.status_code == 422


def test_dashboard_loads_with_health_badge() -> None:
    client, _ = make_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "CityPulse Console" in response.text
    assert "API Health" in response.text
    assert "Elasticsearch" in response.text
    assert "OK" in response.text
    assert "Bucharest" in response.text
    assert "Dubai" in response.text
    assert "<th>country</th>" not in response.text
    assert "<th>region</th>" not in response.text
    assert "theme-toggle" in response.text


def test_dashboard_upsert_renders_result_table() -> None:
    client, _ = make_client()
    response = client.post(
        "/dashboard/upsert",
        data={"city": "Sharjah", "population": "1800000"},
    )
    assert response.status_code == 200
    assert "Sharjah saved successfully." in response.text
    assert "1,800,000" in response.text


def test_dashboard_query_renders_result_table() -> None:
    client, store = make_client()
    store.upsert_city("Abu Dhabi", 1540000)
    response = client.post("/dashboard/query", data={"city": "Abu Dhabi"})
    assert response.status_code == 200
    assert "Found population for Abu Dhabi." in response.text
    assert "1,540,000" in response.text
