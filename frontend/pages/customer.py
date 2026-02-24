import streamlit as st
import requests
from utils.pdf_gen import generate_ticket_pdf
from utils.email_sim import simulate_email_sending

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Customer Portal", layout="wide")
st.title("🎟️ Event Discovery & Booking")

# --- 1. Browse Upcoming Events ---
# Displays only events with 'upcoming' status [cite: 138, 158]
try:
    response = requests.get(f"{API_URL}/events/upcoming")
    if response.status_code == 200:
        events = response.json()
        
        if not events:
            st.info("No upcoming events at the moment. Check back later!")
        
        for event in events:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader(event['name'])
                    st.write(f"**Category:** {event['category']} | **Date:** {event['event_date']}")
                    st.write(f"**Venue ID:** {event['venue_id']}")
                
                with col2:
                    st.write(f"### ${event['ticket_price']}")
                    if st.button(f"View Seats", key=f"view_{event['id']}"):
                        st.session_state.selected_event_id = event['id']
                        st.session_state.event_name = event['name']
                        st.session_state.event_date = event['event_date']
                        st.session_state.price = event['ticket_price']

        # --- 2. Seat Selection & Checkout ---
        if "selected_event_id" in st.session_state:
            st.divider()
            st.header(f"Booking for: {st.session_state.event_name}")
            
            # Fetch available seats for the event [cite: 139]
            ev_id = st.session_state.selected_event_id
            seats_res = requests.get(f"{API_URL}/events/{ev_id}/seats")
            
            if seats_res.status_code == 200:
                available_seats = seats_res.json()
                seat_map = {s['seat_number']: s['id'] for s in available_seats}
                
                selected_labels = st.multiselect(
                    "Select your seats:", 
                    options=list(seat_map.keys()),
                    help=f"You can select up to {event.get('max_tickets_per_user', 5)} seats."  # cite: 62
                )

                if selected_labels:
                    total_cost = len(selected_labels) * st.session_state.price
                    st.write(f"**Total Amount:** ${total_cost}")

                    if st.button("Place Order & Pay"):  # cite: 141-142
                        seat_ids = [seat_map[label] for label in selected_labels]
                        
                        # API call to process booking [cite: 28]
                        booking_payload = {
                            "user_id": 1, # Simulated logged-in user ID
                            "event_id": ev_id,
                            "seat_ids": seat_ids
                        }
                        
                        book_res = requests.post(f"{API_URL}/orders/book", json=booking_payload)
                        
                        if book_res.status_code == 200:
                            order_data = book_res.json()
                            st.success("🎉 Booking Successful!")
                            
                            # Trigger Optional Extensions [cite: 198]
                            ticket_info = {
                                "customer_name": "Valued Customer",
                                "event_name": st.session_state.event_name,
                                "venue_name": "Main Arena",
                                "event_date": st.session_state.event_date,
                                "seat_number": ", ".join(selected_labels),
                                "ticket_code": order_data.get("ticket_code", "TICK-XXXX")
                            }
                            
                            # Extension: Email Simulation [cite: 203]
                            simulate_email_sending("customer@example.com", ticket_info)
                            
                            # Extension: PDF Generation [cite: 202]
                            pdf_bytes = generate_ticket_pdf(ticket_info)
                            st.download_button(
                                label="📥 Download PDF Ticket",
                                data=pdf_bytes,
                                file_name=f"Ticket_{st.session_state.event_name}.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.error(f"Booking failed: {book_res.json().get('detail')}")
            else:
                st.error("Could not load seat map.")

except Exception as e:
    st.error("Backend server is unreachable. Please ensure the FastAPI server is running.")

# --- 3. Request Refund ---
st.divider()
with st.expander("Request a Refund"):
    st.write("Note: Refunds are only allowed before the event date.")  # cite: 158
    refund_order_id = st.number_input("Enter Order ID:", min_value=1, step=1)
    if st.button("Submit Refund Request"):  # cite: 144
        ref_res = requests.post(f"{API_URL}/orders/{refund_order_id}/refund")
        if ref_res.status_code == 200:
            st.warning("Refund processed. Seat availability has been restored.")  # cite: 63, 161
        else:
            st.error(ref_res.json().get('detail'))