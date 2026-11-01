from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterSchema(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)
