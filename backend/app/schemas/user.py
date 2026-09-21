from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password : str 
class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    