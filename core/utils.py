# utils.py

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
import os
from datetime import datetime

def generate_pdf_report(transactions, report_name):
    # Define PDF filename and path
    filename = f"{report_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'reports', filename)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    # Create PDF canvas
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, f"Transaction Report: {report_name}")

    # Table headers
    c.setFont("Helvetica-Bold", 12)
    y = height - 100
    c.drawString(50, y, "Contributor")
    c.drawString(200, y, "Phone")
    c.drawString(300, y, "Amount")
    c.drawString(400, y, "Method")

    # Table rows
    c.setFont("Helvetica", 11)
    for transaction in transactions:
        y -= 20
        c.drawString(50, y, str(transaction.contributor_name))
        c.drawString(200, y, str(transaction.phone_number))
        c.drawString(300, y, f"{transaction.amount} RWF")
        c.drawString(400, y, transaction.payment_method)

        if y < 100:  # Start a new page if space runs out
            c.showPage()
            y = height - 100

    # Finish up
    c.showPage()
    c.save()

    # Return relative media path
    from django.core.files.storage import default_storage
    return default_storage.save(f'reports/{filename}', open(pdf_path, 'rb'))
