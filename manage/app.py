from fastapi import FastAPI

from manage.proxy import proxy_router

app = FastAPI()

app.include_router(proxy_router, prefix="")
