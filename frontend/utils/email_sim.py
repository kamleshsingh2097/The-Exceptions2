import streamlit as st
import time

def simulate_email_sending(customer_email: str, ticket_data: dict):
    """
    Simulates sending an email by displaying a notification and logging 
    the confirmation message.
    """
    with st.spinner(f"Sending confirmation email to {customer_email}..."):
        # Artificial delay to simulate network latency
        time.sleep(1.5) 
        
        confirmation_msg = f"""
        --- EMAIL SIMULATION ---
        To: {customer_email}
        Subject: Booking Confirmed - {ticket_data['event_name']}
        
        Hi {ticket_data['customer_name']},
        
        Your booking for {ticket_data['event_name']} is confirmed!
        Venue: {ticket_data['venue_name']}
        Date & Time: {ticket_data['event_date']}
        Seat: {ticket_data['seat_number']}
        Ticket Code: {ticket_data['ticket_code']}
        
        Please present your ticket code at the gate for entry validation.
        -------------------------
        """
        # Log to terminal for the developer to see during the demo
        print(confirmation_msg)
        
        # Display success in UI
        st.toast(f"Confirmation email sent to {customer_email}!", icon="📧")
        return True
