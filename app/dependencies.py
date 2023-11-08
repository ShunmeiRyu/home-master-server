from jose import jwt
from loguru import logger
from typing import Annotated
from fastapi import Cookie, HTTPException

from configs.auth_conf import auth_settings
from providers import DB


async def get_psql() -> DB:
    db = DB()
    return db


async def get_user_id(authorization: Annotated[str, Cookie()] = None):
    try:
        [type_, token] = authorization.split(" ")
        payload = jwt.decode(
            token=token,
            key=auth_settings.SECRETS_KEY,
            algorithms=[auth_settings.ALGORITHM],
        )
        return payload["id"]
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=401)
