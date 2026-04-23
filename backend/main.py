from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from fastapi.middleware.cors import CORSMiddleware
from dateutil.rrule import rrule, rrulestr, DAILY, WEEKLY, MONTHLY, YEARLY

import crud
import models
import schemas
from database import SessionLocal, engine, get_db

# Create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RemindMe API",
    description="API for a self-hosted task scheduler and reminder application.",
    version="0.0.1",
)

# CORS middleware to allow frontend to connect
origins = [
    "http://localhost",
    "http://localhost:5173", # Default Vite dev server port
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to RemindMe API!"}

@app.post("/events/", response_model=schemas.EventInDB, status_code=status.HTTP_201_CREATED)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    return crud.create_event(db=db, event=event)

@app.get("/events/", response_model=List[schemas.EventInDB])
def read_events(
    skip: int = 0, 
    limit: int = 100, 
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    event_type: Optional[str] = None,
    is_completed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    events = crud.get_events(
        db, 
        skip=skip, 
        limit=limit, 
        start_date=start_date, 
        end_date=end_date,
        event_type=event_type,
        is_completed=is_completed
    )
    return events

@app.get("/events/{event_id}", response_model=schemas.EventInDB)
def read_event(event_id: int, db: Session = Depends(get_db)):
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return db_event

@app.put("/events/{event_id}", response_model=schemas.EventInDB)
def update_event(event_id: int, event: schemas.EventUpdate, db: Session = Depends(get_db)):
    db_event = crud.update_event(db, event_id=event_id, event=event)
    if db_event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return db_event

@app.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    db_event = crud.delete_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return

@app.post("/events/{event_id}/complete", response_model=schemas.EventInDB)
def complete_event(event_id: int, db: Session = Depends(get_db)):
    db_event = crud.complete_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return db_event

# Helper function to generate recurring events for a given date range
# This is a simplified example and might need more robust handling for complex recurrence rules
def get_recurring_events_for_range(
    db: Session, 
    start_date: datetime.date, 
    end_date: datetime.date
) -> List[schemas.EventInDB]:
    recurring_events = db.query(models.Event).filter(models.Event.is_recurring == True).all()
    generated_events = []

    for event in recurring_events:
        if not event.recurrence_pattern or not event.start_date:
            continue

        try:
            # dtstart is crucial for rrule to know when to start generating.
            # Combine start_date with start_time (or midnight if all-day)
            dtstart_combined = datetime.datetime.combine(event.start_date, event.start_time or datetime.time(0,0))
            rule = rrulestr(event.recurrence_pattern, dtstart=dtstart_combined)
            
            # Generate occurrences within the requested range, respecting the event's recurrence_end_date
            for occurrence_dt in rule.between(
                datetime.datetime.combine(start_date, datetime.time.min), 
                datetime.datetime.combine(end_date, datetime.time.max), 
                inc=True # Include start and end dates if they are occurrences
            ):
                # If the occurrence is after the event's recurrence_end_date, skip it
                if event.recurrence_end_date and occurrence_dt.date() > event.recurrence_end_date:
                    continue

                # Create a "virtual" event instance for display
                # This is not stored in DB, but generated on the fly.
                # Note: `is_completed` for recurring instances is generally false,
                # as each instance would need its own completion status if tracked.
                generated_event = schemas.EventInDB(
                    id=event.id, # Use original event ID for reference
                    title=event.title,
                    description=event.description,
                    event_type=event.event_type,
                    start_date=occurrence_dt.date(),
                    start_time=occurrence_dt.time(),
                    end_date=occurrence_dt.date(), # For simplicity, assume same day for recurring instances
                    end_time=event.end_time,
                    is_all_day=event.is_all_day,
                    is_completed=False, # Recurring events are generally not "completed" in this sense
                    created_at=event.created_at,
                    updated_at=event.updated_at,
                    is_recurring=True,
                    recurrence_pattern=event.recurrence_pattern,
                    recurrence_end_date=event.recurrence_end_date
                )
                generated_events.append(generated_event)
        except ValueError as e:
            print(f"Error parsing recurrence rule for event {event.id}: {e}")
            continue
    
    return generated_events

@app.get("/events/today/", response_model=List[schemas.EventInDB])
def get_today_events(date: Optional[datetime.date] = None, db: Session = Depends(get_db)):
    target_date = date or datetime.date.today()
    
    # Get non-recurring events for the target date
    today_events = crud.get_events(db, start_date=target_date, end_date=target_date, is_recurring=False)
    
    # Get recurring events that occur on target date
    recurring_instances = get_recurring_events_for_range(db, target_date, target_date)
    
    # Also include 'todo' items that are not time-bound and not completed
    todo_items = crud.get_events(db, event_type="todo", start_date=None, end_date=None, is_completed=False)
    
    return sorted(today_events + recurring_instances + todo_items, key=lambda e: (e.start_date or datetime.date.min, e.start_time or datetime.time.min))

@app.get("/events/week/", response_model=List[schemas.EventInDB])
def get_week_events(date: Optional[datetime.date] = None, db: Session = Depends(get_db)):
    ref_date = date or datetime.date.today()
    start_of_week = ref_date - datetime.timedelta(days=ref_date.weekday()) # Monday
    end_of_week = start_of_week + datetime.timedelta(days=6) # Sunday

    # Get non-recurring events for the week
    week_events = crud.get_events(db, start_date=start_of_week, end_date=end_of_week, is_recurring=False)

    # Get recurring events that occur this week
    recurring_instances = get_recurring_events_for_range(db, start_of_week, end_of_week)

    # Also include 'todo' items that are not time-bound and not completed
    todo_items = crud.get_events(db, event_type="todo", start_date=None, end_date=None, is_completed=False)

    return sorted(week_events + recurring_instances + todo_items, key=lambda e: (e.start_date or datetime.date.min, e.start_time or datetime.time.min))

@app.get("/events/month/", response_model=List[schemas.EventInDB])
def get_month_events(db: Session = Depends(get_db)):
    today = datetime.date.today()
    start_of_month = today.replace(day=1)
    # Calculate end of month
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - datetime.timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - datetime.timedelta(days=1)

    # Get non-recurring events for the month
    month_events = crud.get_events(db, start_date=start_of_month, end_date=end_of_month, is_recurring=False)

    # Get recurring events that occur this month
    recurring_instances = get_recurring_events_for_range(db, start_of_month, end_of_month)

    # Also include 'todo' items that are not time-bound and not completed
    todo_items = crud.get_events(db, event_type="todo", start_date=None, end_date=None, is_completed=False)

    return sorted(month_events + recurring_instances + todo_items, key=lambda e: (e.start_date or datetime.date.min, e.start_time or datetime.time.min))
