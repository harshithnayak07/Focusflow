from pydantic import BaseModel, ConfigDict, Field

class CreateTask(BaseModel):
    name : str = Field(min_length=1)
    project_id : int
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
class TaskResponse(BaseModel):
    id : int
    name : str
    is_completed : bool
    project_id : int
    owner_id : int
    
    model_config = ConfigDict(from_attributes=True)
    
class TaskUpdate(BaseModel):
    name : str = Field(min_length=1)
    is_completed : bool
    
    model_config = ConfigDict(str_strip_whitespace=True)
