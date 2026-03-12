from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InstanceCreate(BaseModel):
    
    name: str
    type: str 
    os: str
    cpu: int = 1
    ram: int = 512  
    disk: int = 10 
    ssh_key: Optional[str] = None  

class InstanceResponse(BaseModel):
    
    id: int
    name: str
    type: str
    os: str
    status: str
    ssh_port: Optional[int]
    created_at: datetime
    expires_at: Optional[datetime]