from pydantic import BaseModel, Field


class BasicUser(BaseModel):
    email: str = Field(..., max_length=255)


class AuthUser(BasicUser):
    plan_pwd: str = Field(..., min_length=8, max_length=16, validation_alias="password")


class NewUser(BasicUser):
    plan_pwd: str = Field(..., min_length=8, max_length=16, validation_alias="password")


class VerifyData(BasicUser):
    code: str = Field(..., pattern="^[0-9]{6}$")
