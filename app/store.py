from datetime import UTC, datetime
from typing import Any

from elasticsearch import ApiError, Elasticsearch
from elasticsearch import ConnectionError as ElasticsearchConnectionError


class CityNotFoundError(Exception):
    """Raised when a city does not exist in the backing store."""


class StoreUnavailableError(Exception):
    """Raised when Elasticsearch cannot be reached or queried."""


def normalize_city(city: str) -> str:
    return " ".join(city.strip().lower().split())


class CityStore:
    def __init__(self, url: str, index: str) -> None:
        self.index = index
        self.client = Elasticsearch(url)

    def ensure_index(self) -> None:
        try:
            if not self.client.indices.exists(index=self.index):
                self.client.indices.create(
                    index=self.index,
                    mappings={
                        "properties": {
                            "city": {"type": "keyword"},
                            "city_normalized": {"type": "keyword"},
                            "population": {"type": "long"},
                            "updated_at": {"type": "date"},
                        }
                    },
                )
        except (ApiError, ElasticsearchConnectionError) as exc:
            raise StoreUnavailableError(str(exc)) from exc

    def health(self) -> bool:
        try:
            return bool(self.client.ping())
        except ElasticsearchConnectionError:
            return False

    def upsert_city(self, city: str, population: int) -> dict[str, Any]:
        self.ensure_index()
        city_id = normalize_city(city)
        now = datetime.now(UTC).isoformat()
        document = {
            "city": city.strip(),
            "city_normalized": city_id,
            "population": population,
            "updated_at": now,
        }

        try:
            response = self.client.index(
                index=self.index,
                id=city_id,
                document=document,
                refresh=True,
            )
        except (ApiError, ElasticsearchConnectionError) as exc:
            raise StoreUnavailableError(str(exc)) from exc

        return {**document, "status": response.get("result", "updated")}

    def get_city(self, city: str) -> dict[str, Any]:
        self.ensure_index()
        city_id = normalize_city(city)
        try:
            response = self.client.get(index=self.index, id=city_id)
        except ApiError as exc:
            if getattr(exc, "status_code", None) == 404:
                raise CityNotFoundError(city) from exc
            raise StoreUnavailableError(str(exc)) from exc
        except ElasticsearchConnectionError as exc:
            raise StoreUnavailableError(str(exc)) from exc

        source = response.get("_source") or {}
        return {**source, "status": "ok"}

    def seed_default_cities(self, records: list[dict[str, Any]]) -> int:
        self.ensure_index()
        now = datetime.now(UTC).isoformat()
        created = 0

        for record in records:
            city = str(record["city"]).strip()
            city_id = normalize_city(city)
            document = {
                "city": city,
                "city_normalized": city_id,
                "population": int(record["population"]),
                "updated_at": now,
            }
            try:
                self.client.index(index=self.index, id=city_id, document=document, op_type="create")
                created += 1
            except ApiError as exc:
                if getattr(exc, "status_code", None) == 409:
                    continue
                raise StoreUnavailableError(str(exc)) from exc
            except ElasticsearchConnectionError as exc:
                raise StoreUnavailableError(str(exc)) from exc

        if created:
            try:
                self.client.indices.refresh(index=self.index)
            except (ApiError, ElasticsearchConnectionError) as exc:
                raise StoreUnavailableError(str(exc)) from exc

        return created

    def list_cities(self, size: int = 50) -> list[dict[str, Any]]:
        self.ensure_index()
        try:
            response = self.client.search(
                index=self.index,
                size=size,
                sort=[{"updated_at": {"order": "desc"}}],
                query={"match_all": {}},
            )
        except (ApiError, ElasticsearchConnectionError) as exc:
            raise StoreUnavailableError(str(exc)) from exc

        return [
            {**hit.get("_source", {}), "status": "ok"}
            for hit in response.get("hits", {}).get("hits", [])
        ]
