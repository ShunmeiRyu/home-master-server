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
from fastapi import Response
from utils import gen_access_token
from utils import verify_password
from app.schemas.enums import UserStatus
from pydantic import EmailStr

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


@users_router.put("/user/status")
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
        if (datetime.utcnow() - datetime.strptime(verify_info["created_at"], '%Y-%m-%dT%H:%M:%S.%f')).seconds > 60:
            return JSONResponse(
                status_code=403,
                content={"message": "verify_code is timeout"},
            )
        await UserCRUD.update_user_status(db, user_id=db_user["id"])
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


@users_router.get("/user/code")
async def resend_code(email: EmailStr, db=Depends(get_psql)):
    try:
        db_user = await UserCRUD.query_user_with_email(db, email)
        if db_user is None:
            return JSONResponse(
                status_code=400,
                content={"message": "email is not exist"},
            )
        new_verify_code = gen_verify_code()
        send_email(target_eamil=email, verify_code=new_verify_code)
        await UserCRUD.insert_new_user(
            db, user_id=db_user["id"], verify_code=new_verify_code
        )
        return JSONResponse(status_code=200, content={"message": "successful send the code again"})

    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."
            },
        )


@users_router.post("/user/token")
async def login(user: UserSchemas.AuthUser, response: Response, db=Depends(get_psql)):
    try:
        db_user = await UserCRUD.query_user_with_email(db, email=user.email)
        if db_user is None:
            return JSONResponse(
                status_code=400,
                content={"message": "email is not exist"},
            )
        if db_user["status"] == UserStatus.unverify.value:
            return JSONResponse(
                status_code=401,
                content={"message": "email is not verify"},
            )
        if not verify_password(user.plan_pwd, db_user["hashed_pwd"]):
            return JSONResponse(
                status_code=400,
                content={"message": "password is not correct"},
            )

        access_token = gen_access_token(
            payload={
                "id": db_user["id"],
                "email": db_user["email"],
            }
        )
        response.set_cookie(key="access_token", value=access_token)
        return JSONResponse(
            status_code=200,
            content={"message": "successful login"},
        )
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."
            },
        )


@users_router.put("/user/password")
async def change_password(user: UserSchemas.AuthUser, db=Depends(get_psql)):
    try:
        db_user = await UserCRUD.query_user_with_email(db, email=user.email)
        if db_user is None:
            return JSONResponse(
                status_code=400,
                content={"message": "email is not exist"},
            )
        if db_user["status"] == UserStatus.unverify.value:
            return JSONResponse(
                status_code=401,
                content={"message": "email is not verify"},
            )
        if verify_password(user.plan_pwd, db_user["hashed_pwd"]):
            return JSONResponse(
                status_code=400,
                content={"message": "password can not be same as old password"},
            )

        new_hashed_pwd = hash_password(user.plan_pwd)
        await UserCRUD.update_user_password(db, user_id=db_user["id"], new_pwd=new_hashed_pwd)
        return JSONResponse(
            status_code=200,
            content={"message": "successful change password"},
        )
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."
            },
        )
