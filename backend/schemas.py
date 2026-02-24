from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import models

#Venues
class VenueCreate(BaseModel):
    name: str
    city: str
    total_capacity: int
    address: str

class VenueResponse(BaseModel):
    id: int
    name: str
    city: str
    total_capacity: int
    address: str

    class Config:
        from_attributes = True

#Events
class EventCreate(BaseModel):
    venue_id: int
    name: str
    category: str
    event_date: datetime
    ticket_price: float
    max_tickets_per_user: int

class EventStatusUpdate(BaseModel):
    status: models.EventStatus

class EventResponse(BaseModel):
    id: int
    name: str
    category: str
    event_date: datetime
    ticket_price: float
    max_tickets_per_user: int
    status: models.EventStatus
    venue_id: int

    class Config:
        from_attributes = True

#Seats
class SeatResponse(BaseModel):
    id: int
    seat_number: str
    status: models.SeatStatus
    venue_id: int
    event_id: int

    class Config:
        from_attributes = True

#User
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: models.UserRole

    class Config:
        from_attributes = True

#Order
class BookingRequest(BaseModel):
    event_id: int
    seat_ids: List[int]
    payment_mode: Optional[str] = "Simulated"
    card_number: Optional[str] = "4111111111111111"


class AuthRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: models.UserRole = models.UserRole.customer


class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: EmailStr
    role: models.UserRole

class OrderResponse(BaseModel):
    id: int
    total_amount: float
    payment_mode: str
    order_status: models.OrderStatus
    booking_time: datetime
    user_id: int
    event_id: int

    class Config:
        from_attributes = True

#Analytics
class AnalyticsResponse(BaseModel):
    total_tickets_sold: int
    total_revenue: float
