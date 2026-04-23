from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import datetime

class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    event_type: str = Field("task", pattern="^(birthday|bill_payment|task|todo|recurring)$")
    
    start_date: Optional[datetime.date] = None
    start_time: Optional[datetime.time] = None
    end_date: Optional[datetime.date] = None
    end_time: Optional[datetime.time] = None
    
    is_all_day: bool = False
    is_completed: bool = False

    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    recurrence_end_date: Optional[datetime.date] = None

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    pass

class EventInDB(EventBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
