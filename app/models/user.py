from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserRequest(BaseModel):
    email: EmailStr

class UserBase(UserRequest):
    id: Optional[str] = Field(default=None, alias="_id")

    class Config:
        orm_mode = True

class UserResponse(UserRequest):
    pass
    