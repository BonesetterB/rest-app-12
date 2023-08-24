from pydantic import BaseModel, EmailStr, Field,ConfigDict
from datetime  import date



class UserSchema(BaseModel):
    username: str = Field(min_length=5, max_length=26)
    email: EmailStr
    password: str = Field(min_length=6, max_length=20)


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str

    model_config = ConfigDict(from_attributes = True)




class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ContactModel(BaseModel):
    name: str
    surname: str
    email: EmailStr
    phone: str
    birthday:date
    notes:str

class RequestEmail(BaseModel):
    email: EmailStr

class ContactResponse(BaseModel):
    id: int = 1
    name: str
    surname: str
    email: EmailStr
    phone: str
    birthday:date
    notes:str

    model_config = ConfigDict(from_attributes = True)


