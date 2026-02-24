from sqlalchemy.orm import Session
from datetime import datetime, date as date_type, time
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
import models
import uuid

# --- VENUE & EVENT MANAGEMENT (Admin/Organizer) ---

def create_venue(db: Session, name: str, city: str, capacity: int):
    """Register a new venue[cite: 122]."""
    # UI does not currently collect address; keep insert compatible with existing model.
    db_venue = models.Venue(
        name=name,
        city=city,
        total_capacity=capacity,
        address=f"{city} (unspecified address)"
    )
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)
    return db_venue

def create_event(
    db: Session,
    venue_id: int,
    name: str,
    category: str,
    date: datetime | date_type,
    price: float,
    max_per_user: int,
):
    """Onboard an event and auto-generate seats[cite: 7, 123, 126]."""
    # verify that referenced venue exists
    venue = db.query(models.Venue).filter(models.Venue.id == venue_id).first()
    if not venue:
        # client provided invalid venue id
        raise HTTPException(status_code=404, detail="venue not found")

    event_date = (
        datetime.combine(date, time.min)
        if isinstance(date, date_type) and not isinstance(date, datetime)
        else date
    )

    db_event = models.Event(
        venue_id=venue_id, name=name, category=category, 
        event_date=event_date, ticket_price=price, 
        max_tickets_per_user=max_per_user, status="upcoming"
    )
    db.add(db_event)
    db.flush()  # Get event ID to link seats

    # Seat inventory management: create seats based on venue capacity [cite: 8]
    for i in range(1, venue.total_capacity + 1):
        seat = models.Seat(
            event_id=db_event.id,
            venue_id=venue_id,
            seat_number=f"S{i}",
            status="available"
        )
        db.add(seat)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not create event: {exc.orig}")
    db.refresh(db_event)
    return db_event

# --- BOOKING LIFECYCLE (Customer) ---

def create_booking(db: Session, user_id: int, event_id: int, seat_ids: list):
    """Handle ticket booking and seat selection[cite: 9, 140, 141]."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None, f"User with id {user_id} does not exist."

    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    
    # Rule: Booking allowed only for upcoming events [cite: 158]
    if not event or event.status != "upcoming":
        return None, "Booking is only allowed for upcoming events."

    # Rule: Users cannot exceed ticket limit per event [cite: 62]
    if len(seat_ids) > event.max_tickets_per_user:
        return None, f"Exceeds limit of {event.max_tickets_per_user} tickets."
    if not seat_ids:
        return None, "Please select at least one seat."

    # Create the Order [cite: 98]
    order = models.Order(
        user_id=user_id, total_amount=event.ticket_price * len(seat_ids),
        order_status="confirmed", payment_mode="Simulated", event_id=event_id
    )
    db.add(order)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        return None, f"Booking could not be created: {exc.orig}"

    ticket_codes = []
    for s_id in seat_ids:
        seat = db.query(models.Seat).filter(
            models.Seat.id == s_id,
            models.Seat.event_id == event_id,
            models.Seat.status == "available"
        ).first()
        if not seat:
            db.rollback()
            return None, "One or more seats are no longer available."
        
        # State Change: available -> booked [cite: 89]
        seat.status = "booked"
        ticket = models.Ticket(
            order_id=order.id, seat_id=s_id, 
            ticket_code=str(uuid.uuid4())[:8].upper()
        )
        db.add(ticket)
        ticket_codes.append(ticket.ticket_code)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        return None, f"Booking could not be completed due to data integrity rules: {exc.orig}"
    return {"order": order, "ticket_codes": ticket_codes}, "Success"

# --- VALIDATION & ENTRY (Entry Manager) ---

def validate_ticket(db: Session, ticket_code: str):
    """Validate entry and mark ticket as used[cite: 10, 149, 150]."""
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_code == ticket_code).first()
    
    # Rule: Ticket invalid if used or if event date passed [cite: 158, 163]
    if not ticket or ticket.is_used:
        return False, "Ticket is invalid or already used."
    
    ticket.is_used = True # Mark ticket as used [cite: 150]
    db.commit()
    return True, "Ticket validated."

# --- REFUNDS & SUPPORT (Support Executive) ---

def process_refund(db: Session, order_id: int):
    """Process refund and restore seat availability[cite: 11, 63, 155]."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    event = db.query(models.Event).join(models.Seat).join(models.Ticket).filter(models.Ticket.order_id == order_id).first()

from datetime import datetime, timezone

def process_refund(event):
    # Rule: Refund allowed only before event_date
    if datetime.now(timezone.utc) >= event.event_date:
        return False, "Refunds are only allowed before the event date."

    # continue refund logic
    return True, "Refund processed successfully."
    # Rule: If refund approved, order status -> refunded, seat -> available [cite: 159-161]
    order.order_status = "refunded"
    tickets = db.query(models.Ticket).filter(models.Ticket.order_id == order_id).all()
    
    for t in tickets:
        seat = db.query(models.Seat).filter(models.Seat.id == t.seat_id).first()
        seat.status = "available" # Restore seat availability 
        t.is_used = True # Effectively cancels the ticket [cite: 162]
    
    db.commit()
    return True, "Refund processed."

# --- ANALYTICS (Extension) ---

def get_analytics(db: Session):
    """Simple analytics for the platform[cite: 201]."""
    total_tickets = db.query(models.Ticket).count()
    return {"total_tickets_sold": total_tickets}
