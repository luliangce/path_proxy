from fastapi import APIRouter

demo_router = APIRouter()


@demo_router.get("/hello")
async def helloworld():
    return {"hello": "world"}
