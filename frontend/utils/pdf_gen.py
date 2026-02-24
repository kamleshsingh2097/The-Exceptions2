try:
    from fpdf import FPDF
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Missing dependency 'fpdf2'. Install it with `pip install fpdf2` "
        "or `pip install -r requirementf.txt`."
    ) from exc

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
    pdf.cell(0, 10, f"Date & Time: {ticket_data['event_date']}", 0, 1)
    pdf.cell(0, 10, f"Seat Number: {ticket_data['seat_number']}", 0, 1)
    pdf.cell(0, 10, f"Order ID: {ticket_data.get('order_id', 'N/A')}", 0, 1)
    
    pdf.ln(10)
    
    # Unique Ticket Code Section
    ticket_codes = ticket_data.get("ticket_codes")
    if not ticket_codes:
        ticket_codes = [ticket_data.get("ticket_code", "TICK-XXXX")]

    pdf.set_fill_color(230, 230, 230)
    pdf.set_font('Arial', 'B', 14)
    if len(ticket_codes) == 1:
        pdf.cell(0, 15, f"TICKET CODE: {ticket_codes[0]}", 0, 1, 'C', fill=True)
    else:
        pdf.cell(0, 12, "TICKET CODES", 0, 1, 'C', fill=True)
        pdf.set_font('Arial', 'B', 12)
        for code in ticket_codes:
            pdf.cell(0, 9, code, 0, 1, 'C')

    pdf.ln(10)
    
    # Instructions for Entry Manager [cite: 146-151]
    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 10, "Present this code at the entry gate for validation. "
                          "The Entry Manager will mark this ticket as used upon entry.")

    # Return PDF bytes for Streamlit download. fpdf2 may return bytearray/bytes.
    raw_output = pdf.output(dest='S')
    if isinstance(raw_output, (bytes, bytearray)):
        return bytes(raw_output)
    return raw_output.encode('latin-1')
