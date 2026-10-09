from pydantic import BaseModel, ConfigDict, Field

class ProjectCreate(BaseModel):
    name : str = Field(min_length=1)
    description : str | None = None
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
class ProjectResponse(BaseModel):
    id : int
    name : str
    description : str | None = None
    owner_id : int
    
    model_config = ConfigDict(from_attributes=True)
    
class ProjectUpdate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    
    model_config = ConfigDict(str_strip_whitespace=True)