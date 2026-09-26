from datetime import datetime
from pydantic import BaseModel

class EventCreate(BaseModel):
    name: str
    venue: str
    start_time: datetime

class EventResponse(BaseModel):
    id: str
    name: str
    venue: str
    start_time: datetime
    class Config:
        from_attributes = True

'''
this function / schema specifies the format of db data sent or recived by api
'''