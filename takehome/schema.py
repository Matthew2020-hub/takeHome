from pydantic import BaseModel, Field, EmailStr



class Registration(BaseModel):
 
    firstName: str = Field(..., max_length=50, min_length=1)
    lastName: str = Field(..., max_length=50, min_length=1)
    password: int = Field(..., ge=0, le=10)
    email: EmailStr



class Login(BaseModel):
  
    password:str = Field(...) 
    email: EmailStr


class Template(BaseModel):
    template_name: str = Field(..., max_length=50)
    body: str = Field(..., max_length=500)
    subject: str = Field(..., max_length=500)