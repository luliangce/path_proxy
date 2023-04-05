from fastapi import FastAPI

from manage.demo import demo_router
from manage.proxy import proxy_router

app = FastAPI()

app.include_router(proxy_router, prefix="")
app.include_router(demo_router, prefix="/demo")
