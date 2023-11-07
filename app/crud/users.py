from typing import Optional
from providers.postgresql import DB
from app.schemas.enums import UserStatus


async def query_user_with_email(
    db: DB,
    /,
    email: str,
) -> Optional[dict]:
    sql = f"""
    SELECT
        id,
        hashed_pwd
    FROM
        users
    WHERE
        users.email = '{email}';
    """
    return await db.fetch_one(sql)


async def insert_new_user(
    db: DB,
    /,
    email: str,
    hashed_pwd: str,
):
    sql = f"""
    INSERT INTO USERS (email, hashed_pwd, status)
    VALUES ('{email}', '{hashed_pwd}', '{UserStatus.unverify.value}')
    RETURNING id
    """
    return await db.fetch_one(sql)


async def insert_verify_code(db: DB, /, user_id: str, verify_code: str):
    sql = f"""
    INSERT INTO VERIFY_CODES (user_id, verify_code)
    VALUES ('{user_id}', '{verify_code}')
    """

    await db.execute(sql)


async def query_verify_info(db: DB, /, user_id: str, verify_code: str):
    sql = f"""
    SELECT
        verify_code,
        created_at
    FROM
        VERIFY_CODES
    WHERE
        user_id = '{user_id}'
        AND
        verify_code = '{verify_code}';
    """

    return await db.fetch_one(sql)


