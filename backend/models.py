from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


# ---------------- ENUMS ---------------- #

class EventStatus(str, enum.Enum):
    upcoming = "upcoming"
    closed = "closed"
    cancelled = "cancelled"


class SeatStatus(str, enum.Enum):
    available = "available"
    booked = "booked"


class UserRole(str, enum.Enum):
    admin = "admin"
    organizer = "organizer"
    customer = "customer"
    entry_manager = "entry_manager"
    support = "support"


class OrderStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    refunded = "refunded"


class SupportRequestStatus(str, enum.Enum):
    pending = "pending"
    processed = "processed"
    rejected = "rejected"


# ---------------- MODELS ---------------- #

class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    total_capacity = Column(Integer, nullable=False)
    address = Column(String, nullable=False)

    events = relationship("Event", back_populates="venue")
    seats = relationship("Seat", back_populates="venue")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    ticket_price = Column(Float, nullable=False)
    max_tickets_per_user = Column(Integer, nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.upcoming)

    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)

    venue = relationship("Venue", back_populates="events")
    orders = relationship("Order", back_populates="event")
    seats = relationship("Seat", back_populates="event")


class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    seat_number = Column(String, nullable=False)
    status = Column(Enum(SeatStatus), default=SeatStatus.available)

    venue_id = Column(Integer, ForeignKey("venues.id"))
    event_id = Column(Integer, ForeignKey("events.id"))

    venue = relationship("Venue", back_populates="seats")
    event = relationship("Event", back_populates="seats")
    tickets = relationship("Ticket", back_populates="seat")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.customer)

    orders = relationship("Order", back_populates="user")
    support_requests = relationship("SupportRequest", back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    total_amount = Column(Float, nullable=False)
    payment_mode = Column(String, nullable=False)
    order_status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    booking_time = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)

    user = relationship("User", back_populates="orders")
    event = relationship("Event", back_populates="orders")
    tickets = relationship("Ticket", back_populates="order")
    support_requests = relationship("SupportRequest", back_populates="order")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_code = Column(String, unique=True, nullable=False, index=True)
    is_used = Column(Boolean, default=False, nullable=False)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id"), nullable=False)

    order = relationship("Order", back_populates="tickets")
    seat = relationship("Seat", back_populates="tickets")


class SupportRequest(Base):
    __tablename__ = "support_requests"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_note = Column(String, nullable=True)
    status = Column(Enum(SupportRequestStatus), default=SupportRequestStatus.pending, nullable=False)
    resolution_note = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="support_requests")
    order = relationship("Order", back_populates="support_requests")
