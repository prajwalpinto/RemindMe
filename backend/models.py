from sqlalchemy import Column, Integer, String, Boolean, Date, Time, DateTime
from sqlalchemy.sql import func
from database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    event_type = Column(String, default="task") # e.g., 'birthday', 'bill_payment', 'task', 'todo', 'recurring'
    
    start_date = Column(Date, nullable=True)
    start_time = Column(Time, nullable=True)
    end_date = Column(Date, nullable=True)
    end_time = Column(Time, nullable=True)
    
    is_all_day = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False) # For tasks/todos
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String, nullable=True) # Stores rrule string, e.g., "FREQ=WEEKLY;INTERVAL=2;BYDAY=SA"
    recurrence_end_date = Column(Date, nullable=True) # Optional end date for recurrence

    def __repr__(self):
        return f"<Event(id={self.id}, title='{self.title}', start_date={self.start_date})>"
