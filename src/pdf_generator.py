from fpdf import FPDF
import os

class PDFGenerator:
    @staticmethod
    def generate_invoice(booking_data):
        """
        Generates a PDF invoice for a booking.
        booking_data should be a dictionary containing:
        - id, first_name, last_name, passport_no, email, phone
        - service_type, destination, start_date, end_date, provider
        - total_cost, selling_price, status
        """
        pdf = FPDF()
        pdf.add_page()

        # Logo / Header
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 10, "Agence de Voyage - Invoice", ln=True, align='C')
        pdf.ln(10)

        # Agency Details
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, "123 Travel St, Paris, France", ln=True, align='C')
        pdf.cell(0, 10, "Contact: +33 1 23 45 67 89 | contact@agency.com", ln=True, align='C')
        pdf.ln(20)

        # Invoice Info
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Invoice #{booking_data['id']}", ln=True)
        pdf.ln(5)

        # Client Details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Client Information:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Name: {booking_data['first_name']} {booking_data['last_name']}", ln=True)
        pdf.cell(0, 10, f"Passport: {booking_data['passport_no']}", ln=True)
        pdf.cell(0, 10, f"Email: {booking_data['email']}", ln=True)
        pdf.cell(0, 10, f"Phone: {booking_data['phone']}", ln=True)
        pdf.ln(10)

        # Booking Details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Booking Details:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Service: {booking_data['service_type']}", ln=True)
        pdf.cell(0, 10, f"Destination: {booking_data['destination']}", ln=True)
        pdf.cell(0, 10, f"Provider: {booking_data['provider']}", ln=True)
        pdf.cell(0, 10, f"Dates: {booking_data['start_date']} to {booking_data['end_date']}", ln=True)
        pdf.ln(10)

        # Financials
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Total Amount Due: ${booking_data['selling_price']:.2f}", ln=True, align='R')
        pdf.set_font("Arial", "I", 12)
        pdf.cell(0, 10, f"Status: {booking_data['status']}", ln=True, align='R')

        # Output
        filename = f"invoice_{booking_data['id']}_{booking_data['last_name']}.pdf"
        pdf.output(filename)
        return os.path.abspath(filename)
