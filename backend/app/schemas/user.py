from pydantic import BaseModel, ConfigDict, Field, EmailStr

class UserCreate(BaseModel):
    name : str = Field(min_length=1)
    email : EmailStr
    password : str = Field(min_length=8)
    
    model_config = ConfigDict(str_strip_whitespace=True)

class UserResponse(BaseModel):
    id : int
    name : str
    email : str
    role : str
    is_active : bool
    
    model_config = ConfigDict(from_attributes=True)
    
class UserUpdate(BaseModel):
    name : str = Field(min_length=1)
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
class Userlogin(BaseModel):
    email : str
    password : str
    
class Token(BaseModel):
    access_token : str
    token_type : str