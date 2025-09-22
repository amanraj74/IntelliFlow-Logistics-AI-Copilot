from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.api.routers import drivers, incidents, alerts
from backend.api.routers import ai_query_pathway as ai_query


def create_app() -> FastAPI:
    app = FastAPI(
        title="IntelliFlow Logistics AI API", 
        version="0.1.0",
        description="Real-time logistics intelligence system"
    )

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

    @app.get("/")
    def root():
        return {"message": "IntelliFlow Logistics AI API", "version": "0.1.0"}

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "service": "IntelliFlow Logistics AI"}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )