import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: Literal["admin", "member", "viewer"] = "member"


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)