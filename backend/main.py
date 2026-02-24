from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, database, crud
from datetime import datetime
from database import get_db
# Initialize Database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Online Event Ticket Booking Platform API")


# --- PLATFORM ADMIN / ORGANIZER ENDPOINTS ---

@app.post("/admin/venues/", tags=["Admin"])
def add_venue(name: str, city: str, capacity: int, db: Session = Depends(get_db)):
    """Add a new venue to the platform[cite: 122]."""
    return crud.create_venue(db, name=name, city=city, capacity=capacity)

@app.post("/admin/events/", tags=["Admin"])
def add_event(
    venue_id: int, 
    name: str, 
    category: str, 
    date: datetime, 
    price: float, 
    max_per_user: int, 
    db: Session = Depends(get_db)
):
    """Create a new event and auto-generate seats[cite: 123, 126]."""
    return crud.create_event(db, venue_id, name, category, date, price, max_per_user)

@app.patch("/admin/events/{event_id}/status", tags=["Admin"])
def update_event_status(event_id: int, status: str, db: Session = Depends(get_db)):
    """Update event status to 'upcoming', 'closed', or 'cancelled'[cite: 77, 124]."""
    return crud.update_event_status(db, event_id, status)

# --- CUSTOMER ENDPOINTS ---

@app.get("/events/upcoming", tags=["Customer"])
def list_upcoming_events(db: Session = Depends(get_db)):
    """Browse events that are open for booking[cite: 138, 158]."""
    return db.query(models.Event).filter(models.Event.status == "upcoming").all()

@app.get("/events/{event_id}/seats", tags=["Customer"])
def get_available_seats(event_id: int, db: Session = Depends(get_db)):
    """View seat inventory for a specific event[cite: 139]."""
    return db.query(models.Seat).filter(
        models.Seat.event_id == event_id, 
        models.Seat.status == "available"
    ).all()

@app.post("/orders/book", tags=["Customer"])
def book_seats(user_id: int, event_id: int, seat_ids: List[int], db: Session = Depends(get_db)):
    """Handle the booking flow and seat selection [cite: 140-141]."""
    order, message = crud.create_booking(db, user_id, event_id, seat_ids)
    if not order:
        raise HTTPException(status_code=400, detail=message)
    return {"message": "Booking confirmed", "order": order}

@app.post("/orders/{order_id}/refund", tags=["Customer"])
def request_refund(order_id: int, db: Session = Depends(get_db)):
    """Process a refund request before the event date."""
    success, message = crud.process_refund(db, order_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

# --- ENTRY MANAGER ENDPOINTS ---

@app.post("/tickets/validate", tags=["Entry Manager"])
def validate_ticket(ticket_code: str, db: Session = Depends(get_db)):
    """Validate entry and mark ticket as used [cite: 149-150]."""
    success, message = crud.validate_ticket(db, ticket_code)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

# --- SUPPORT & ANALYTICS ---

@app.get("/admin/analytics", tags=["Support/Analytics"])
def get_platform_analytics(db: Session = Depends(get_db)):
    """Extension: View total tickets sold and revenue[cite: 201]."""
    return crud.get_analytics(db)