from fastapi import FastAPI

from app.api.routes.search import router as search_router
from app.config import load_dotenv
from app.logging_config import configure_logging


load_dotenv()
configure_logging()

app = FastAPI(
    title="EasyTicket API",
    description="Backend API for the EasyTicket AI ticket search agent.",
    version="0.1.0",
)

app.include_router(search_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
