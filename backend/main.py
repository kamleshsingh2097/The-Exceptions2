from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
import models, database, crud
import schemas
import auth
from datetime import datetime
from database import get_db
# Initialize Database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Online Event Ticket Booking Platform API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# --- AUTH ENDPOINTS ---

@app.post("/auth/register", response_model=schemas.AuthTokenResponse, tags=["Auth"])
def register(payload: schemas.AuthRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        name=payload.name,
        email=payload.email,
        password=auth.hash_password(payload.password),
        role=payload.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"user_id": user.id, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }


@app.post("/auth/login", response_model=schemas.AuthTokenResponse, tags=["Auth"])
def login(payload: schemas.AuthLoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not auth.verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = auth.create_access_token({"user_id": user.id, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }


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
def book_seats(
    payload: schemas.BookingRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle the booking flow and seat selection [cite: 140-141]."""
    result, message, status_code = crud.create_booking(db, current_user.id, payload.event_id, payload.seat_ids)
    if not result:
        raise HTTPException(status_code=status_code, detail=message)
    order = result["order"]
    return {
        "message": "Booking confirmed",
        "order_id": order.id,
        "order": {
            "id": order.id,
            "event_id": order.event_id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "order_status": str(order.order_status),
            "payment_mode": order.payment_mode,
        },
        "ticket_codes": result["ticket_codes"]
    }


@app.post("/book-seat", tags=["Customer"])
def book_single_seat(
    event_id: int,
    seat_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Book a single seat with pessimistic row locking."""
    result, message, status_code = crud.create_booking(db, current_user.id, event_id, [seat_id])
    if not result:
        raise HTTPException(status_code=status_code, detail=message)
    return {
        "status": "success",
        "order_id": result["order"].id,
        "ticket_code": result["ticket_codes"][0] if result["ticket_codes"] else None
    }

@app.post("/orders/{order_id}/refund", tags=["Customer"])
def request_refund(
    order_id: int,
    review_note: str | None = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a refund request before the event date."""
    success, message = crud.process_refund(db, order_id, current_user.id, review_note)
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


@app.get("/support/refund-requests", tags=["Support/Analytics"])
def get_refund_requests(db: Session = Depends(get_db)):
    """View customer refund requests with review notes and resolution status."""
    return crud.list_support_requests(db)
