import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.config import get_settings
from app.core.request_context import RequestContextMiddleware

# Rend visibles les logs applicatifs (ex. e-mails journalisés sans SMTP).
logging.basicConfig(level=logging.INFO)

settings = get_settings()

app = FastAPI(title="IUMC API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)

app.include_router(api_v1_router, prefix=settings.api_prefix)
