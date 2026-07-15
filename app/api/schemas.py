from pydantic import BaseModel, EmailStr 

class UserSchema(BaseModel):
    id : int
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id : int
    email: EmailStr

class UserDB(UserSchema)
    id: int