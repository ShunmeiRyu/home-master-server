from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from configs import app_settings
from providers import init_logging
from providers import DB

from app.endpoints.users import users_router


# スタートアップ前のイベント
@asynccontextmanager
async def lifespan(app: FastAPI):
    # グローバルログの初期化
    init_logging()
    # データベースプールの初期化
    await DB().connect()
    yield


# アプリ設定
app = FastAPI(
    title=app_settings.NAME,
    docs_url=app_settings.DOCS,
    openapi_url=app_settings.OPENAPI,
    lifespan=lifespan,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTER追加
app.include_router(users_router)

if __name__ == "__main__":
    from uvicorn import run

    run(app="main:app", host="0.0.0.0", port=8000, reload=True)
