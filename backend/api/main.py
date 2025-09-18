from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import drivers, incidents, alerts, ai_query


def create_app() -> FastAPI:
    app = FastAPI(title="IntelliFlow Logistics AI API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(drivers.router, prefix="/drivers", tags=["drivers"])
    app.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
    app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
    app.include_router(ai_query.router, prefix="/ai", tags=["ai"])

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()


