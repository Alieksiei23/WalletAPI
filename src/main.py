from prometheus_fastapi_instrumentator import Instrumentator

from fastapi import FastAPI
from src.api.v1 import analytics_router, transaction_router, user_router


app = FastAPI()

Instrumentator().instrument(app).expose(app)

app.include_router(user_router)
app.include_router(analytics_router)
app.include_router(transaction_router)
