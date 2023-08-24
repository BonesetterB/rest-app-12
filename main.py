from fastapi import FastAPI,Request,status
from ipaddress import ip_address
from fastapi.staticfiles import StaticFiles
from src.routes import contacts,auth,users
import uvicorn
from fastapi.responses import JSONResponse
from typing import Callable
import re
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from src.conf.config import config
import redis.asyncio as redis

app= FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_IPS = [ip_address('192.168.1.0'), ip_address('172.16.0.0'), ip_address("127.0.0.1")]


@app.middleware("http")
async def limit_access_by_ip(request: Request, call_next: Callable):
    """
    Middleware to limit access by IP address.

    :param request: HTTP request.
    :type request: Request
    :param call_next: Callable to call the next middleware or endpoint handler.
    :type call_next: Callable
    :return: Response from the next middleware or endpoint handler.
    """
    ip = ip_address(request.client.host)
    if ip not in ALLOWED_IPS:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
    response = await call_next(request)
    return response


user_agent_ban_list = [r"Python-urllib"]


@app.middleware("http")
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    """
    Middleware to ban user agents.

    :param request: HTTP request.
    :type request: Request
    :param call_next: Callable to call the next middleware or endpoint handler.
    :type call_next: Callable
    :return: Response from the next middleware or endpoint handler.
    """
    user_agent = request.headers.get("user-agent")
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
    response = await call_next(request)
    return response

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(contacts.router)
app.include_router(auth.router)
app.include_router(users.router)

@app.on_event("startup")
async def startup():
    r = await redis.Redis(host=config.redis_host, port=config.redis_port, db=0, encoding="utf-8",
                          password=config.redis_password)
    await FastAPILimiter.init(r)

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", reload=True, log_level="info")