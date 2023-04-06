import urllib.parse

from fastapi import APIRouter, Path, Request
from fastapi.responses import PlainTextResponse, StreamingResponse
from httpx import AsyncClient

proxy_router = APIRouter()


@proxy_router.api_route(
    "/{target:path}",
    methods=["GET", "POST", "PUT", "HEAD", "PATCH", "DELETE", "OPTIONS"],
)
async def porxy(request: Request, target: str = Path(...)):
    try:
        u = urllib.parse.urlparse(target)
        if not u.scheme.startswith("http"):
            referer = request.headers.get("referer")
            if not referer:
                raise Exception("no referer and hostname")

            parent = urllib.parse.urlparse(referer).path
            if parent.startswith("/"):
                parent = parent[1:]

            parent_url = urllib.parse.urlparse(parent)
            if not parent_url.hostname:
                raise Exception("no referer and hostname")
            target = urllib.parse.urljoin(
                parent,
                u.path,
            )

    except Exception as e:
        return PlainTextResponse(status_code=500, content=f"无法处理代理链接{target}:{e}")
    headers = {**request.headers}
    if hostname := urllib.parse.urlparse(target).hostname:
        headers["host"] = hostname
    client = AsyncClient(timeout=10, follow_redirects=True)

    await client.__aenter__()
    remote_request = client.build_request(
        method=request.method,
        url=target,
        headers=headers,
    )
    remote_response = await client.send(request=remote_request, stream=True)

    async def iterator():
        async for i in remote_response.aiter_raw():
            yield i
        await client.__aexit__()

    return StreamingResponse(
        content=iterator(),
        status_code=remote_response.status_code,
        headers=remote_response.headers,
    )
