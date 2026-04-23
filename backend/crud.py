from sqlalchemy.orm import Session
import models
import schemas
import datetime
from typing import List, Optional

def get_event(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def get_events(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    event_type: Optional[str] = None,
    is_completed: Optional[bool] = None,
    is_recurring: Optional[bool] = None # Added for filtering non-recurring events
) -> List[models.Event]:
    query = db.query(models.Event)
    
    if start_date:
        query = query.filter(models.Event.start_date >= start_date)
    if end_date:
        query = query.filter(models.Event.start_date <= end_date)
    if event_type:
        query = query.filter(models.Event.event_type == event_type)
    if is_completed is not None:
        query = query.filter(models.Event.is_completed == is_completed)
    if is_recurring is not None:
        query = query.filter(models.Event.is_recurring == is_recurring)
        
    return (
        query.order_by(models.Event.start_date.asc(), models.Event.start_time.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_event(db: Session, event: schemas.EventCreate):
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_event(db: Session, event_id: int, event: schemas.EventUpdate):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        update_data = event.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_event, key, value)
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
    return db_event

def delete_event(db: Session, event_id: int):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        db.delete(db_event)
        db.commit()
    return db_event

def complete_event(db: Session, event_id: int):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        db_event.is_completed = True
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
    return db_event
