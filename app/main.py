from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.config import Settings, get_settings
from app.seed_data import DEFAULT_CITY_RECORDS
from app.store import CityNotFoundError, CityStore, StoreUnavailableError


class CityPopulationRequest(BaseModel):
    population: int = Field(..., ge=0, description="City population")


class CityPopulationResponse(BaseModel):
    city: str
    population: int
    status: str
    updated_at: str | None = None


def create_store(settings: Annotated[Settings, Depends(get_settings)]) -> CityStore:
    return CityStore(settings.elasticsearch_url, settings.elasticsearch_index)


app = FastAPI(title="CityPulse", version="1.1.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/healthz", response_class=PlainTextResponse, tags=["health"])
def healthz() -> str:
    return "OK"


@app.get("/readyz", tags=["health"])
def readyz(store: Annotated[CityStore, Depends(create_store)]) -> dict[str, str]:
    if not store.health():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Elasticsearch is unavailable",
        )
    return {"status": "ready"}


@app.put("/cities/{city}", response_model=CityPopulationResponse, tags=["cities"])
def upsert_city(
    city: str,
    payload: CityPopulationRequest,
    store: Annotated[CityStore, Depends(create_store)],
) -> dict[str, object]:
    if not city.strip():
        raise HTTPException(status_code=422, detail="City name cannot be empty")
    try:
        return store.upsert_city(city, payload.population)
    except StoreUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from exc


@app.get("/cities/{city}", response_model=CityPopulationResponse, tags=["cities"])
def get_city(
    city: str,
    store: Annotated[CityStore, Depends(create_store)],
) -> dict[str, object]:
    if not city.strip():
        raise HTTPException(status_code=422, detail="City name cannot be empty")
    try:
        return store.get_city(city)
    except CityNotFoundError as exc:
        raise HTTPException(status_code=404, detail="City not found") from exc
    except StoreUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from exc


def _dashboard_context(
    request: Request,
    store: CityStore,
    message: str | None = None,
    error: str | None = None,
    result: dict[str, object] | None = None,
) -> dict[str, object]:
    db_healthy = store.health()
    rows: list[dict[str, object]] = []
    if db_healthy:
        try:
            store.seed_default_cities(DEFAULT_CITY_RECORDS)
            rows = store.list_cities()
        except StoreUnavailableError:
            db_healthy = False

    if result and not rows:
        rows = [result]

    return {
        "request": request,
        "message": message,
        "error": error,
        "result": result,
        "rows": rows,
        "db_healthy": db_healthy,
    }


@app.get("/", response_class=HTMLResponse, tags=["dashboard"])
def dashboard(
    request: Request,
    store: Annotated[CityStore, Depends(create_store)],
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        _dashboard_context(request, store),
    )


@app.post("/dashboard/upsert", response_class=HTMLResponse, tags=["dashboard"])
def dashboard_upsert(
    request: Request,
    city: Annotated[str, Form()],
    population: Annotated[int, Form(ge=0)],
    store: Annotated[CityStore, Depends(create_store)],
) -> HTMLResponse:
    try:
        result = store.upsert_city(city, population)
        return templates.TemplateResponse(
            request,
            "index.html",
            _dashboard_context(
                request,
                store,
                message=f"{result['city']} saved successfully.",
                result=result,
            ),
        )
    except StoreUnavailableError:
        return templates.TemplateResponse(
            request,
            "index.html",
            _dashboard_context(request, store, error="Database is unavailable."),
            status_code=503,
        )


@app.post("/dashboard/query", response_class=HTMLResponse, tags=["dashboard"])
def dashboard_query(
    request: Request,
    city: Annotated[str, Form()],
    store: Annotated[CityStore, Depends(create_store)],
) -> HTMLResponse:
    try:
        result = store.get_city(city)
        return templates.TemplateResponse(
            request,
            "index.html",
            _dashboard_context(
                request,
                store,
                message=f"Found population for {result['city']}.",
                result=result,
            ),
        )
    except CityNotFoundError:
        return templates.TemplateResponse(
            request,
            "index.html",
            _dashboard_context(request, store, error=f"{city} was not found."),
            status_code=404,
        )
    except StoreUnavailableError:
        return templates.TemplateResponse(
            request,
            "index.html",
            _dashboard_context(request, store, error="Database is unavailable."),
            status_code=503,
        )
