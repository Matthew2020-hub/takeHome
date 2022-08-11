from typing import Optional
from pydantic import BaseModel, Field, EmailStr



class Registration(BaseModel):
    firstName: str 
    lastName: str 
    password: str
    email: EmailStr

class Login(BaseModel):
    password:str = Field(...) 
    email: EmailStr


class Template(BaseModel):
    template_name: str = Field(..., max_length=50)
    body: str = Field(..., max_length=500)
    subject: str = Field(..., max_length=500)


class UpdateTemplate(BaseModel):
    template_name: Optional[str] = None
    body: Optional[str] = None
    subject: Optional[str] = None
