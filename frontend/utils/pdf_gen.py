from fpdf import FPDF
from datetime import datetime
import io

class TicketPDF(FPDF):
    def header(self):
        # Professional Header for the Ticket
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'ONLINE EVENT TICKET', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        # Footer with validation note
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'This ticket is invalid after the event date or once marked as used.', 0, 0, 'C')

def generate_ticket_pdf(ticket_data: dict):
    """
    Generates a PDF byte stream for a ticket.
    Expected ticket_data keys: event_name, ticket_code, seat_number, venue_name, event_date
    """
    pdf = TicketPDF()
    pdf.add_page()
    
    # Event Details Section
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Event: {ticket_data['event_name']}", 0, 1)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Venue: {ticket_data['venue_name']}", 0, 1)
    pdf.cell(0, 10, f"Date: {ticket_data['event_date']}", 0, 1)
    pdf.cell(0, 10, f"Seat Number: {ticket_data['seat_number']}", 0, 1)
    
    pdf.ln(10)
    
    # Unique Ticket Code Section 
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 15, f"TICKET CODE: {ticket_data['ticket_code']}", 0, 1, 'C', fill=True)
    
    pdf.ln(10)
    
    # Instructions for Entry Manager [cite: 146-151]
    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 10, "Present this code at the entry gate for validation. "
                          "The Entry Manager will mark this ticket as used upon entry.")

    # Return the PDF as a byte stream for Streamlit download
    return pdf.output(dest='S').encode('latin-1')