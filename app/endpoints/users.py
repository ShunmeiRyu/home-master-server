from loguru import logger
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from app.dependencies import get_psql
from app.schemas import users as UserSchemas
from app.crud import users as UserCRUD
from utils import hash_password
from utils import gen_verify_code
from utils import send_email

users_router = APIRouter()


@users_router.post("/user")
async def register(new_user: UserSchemas.NewUser, db=Depends(get_psql)):
    try:
        db_user = await UserCRUD.query_user_with_email(db, email=new_user.email)

        if db_user:
            return JSONResponse(
                status_code=400,
                content={"message": "email is exist"},
            )

        new_db_user = await UserCRUD.insert_new_user(
            db,
            email=new_user.email,
            hashed_pwd=(hash_password(new_user.plan_pwd)),
        )

        new_verify_code = gen_verify_code()

        send_email(target_eamil=new_user.email, verify_code=new_verify_code)

        await UserCRUD.insert_verify_code(
            db, user_id=new_db_user["id"], verify_code=new_verify_code
        )

        return JSONResponse(status_code=200, content={"message": "successful created"})

    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."
            },
        )


@users_router.post("/user/verify_code")
async def verify_email(verify_data: UserSchemas.VerifyData, db=Depends(get_psql)):
    try:
        db_user = await UserCRUD.query_user_with_email(db, email=verify_data.email)
        if db_user is None:
            return JSONResponse(
                status_code=400,
                content={"message": "email is not exist"},
            )
        verify_info = await UserCRUD.query_verify_info(
            db, user_id=db_user["id"], verify_code=verify_data.code
        )
        if verify_info is None:
            return JSONResponse(
                status_code=400,
                content={"message": "verify_code is not exist"},
            )

        if (datetime.now() - verify_info["created_at"]).seconds > 60:
            return JSONResponse(
                status_code=403,
                content={"message": "verify_code is timeout"},
            )

        return JSONResponse(
            status_code=200,
            content={"message": "verify_code is ok"},
        )
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."
            },
        )
