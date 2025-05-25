from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfMerger
import os
from datetime import datetime

def generate_quote_pdf(name, details, price, original_price, quote_quality, image_paths, output_path, cover_path=None):
    tmp_path = "tmp_quote.pdf"
    c = canvas.Canvas(tmp_path, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, f"Window Knight Quote Summary - {datetime.today().strftime('%Y-%m-%d')}")
    c.drawString(50, 730, f"Client: {name}")
    c.drawString(50, 710, f"Quality Assessment: {quote_quality}")
    c.drawString(50, 690, f"AI Price: ${price} (Original: ${original_price})")

    c.drawString(50, 660, "Quote Summary:")
    text = c.beginText(50, 640)
    text.setFont("Helvetica", 10)
    for line in details.split(','):
        text.textLine(f"- {line.strip()}")
    c.drawText(text)

    if image_paths:
        y = 400
        for img in image_paths[:3]:  # Limit to 3 images
            c.drawImage(img, 50, y, width=120, height=90)
            y -= 100

    c.showPage()
    c.save()

    if cover_path:
        merger = PdfMerger()
        merger.append(cover_path)
        merger.append(tmp_path)
        merger.write(output_path)
        merger.close()
        os.remove(tmp_path)
    else:
        os.rename(tmp_path, output_path)


def generate_customer_pdf(name, details, image_paths, output_path, cover_path=None):
    tmp_path = "tmp_customer_quote.pdf"
    c = canvas.Canvas(tmp_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, "🧼 The Window Knight")
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, f"Quote Request Summary - {datetime.today().strftime('%Y-%m-%d')}")
    c.drawString(50, 710, f"Client: {name}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 680, "Your Job Request Includes:")
    text = c.beginText(50, 660)
    text.setFont("Helvetica", 10)
    for line in details.split(','):
        text.textLine(f"- {line.strip()}")
    c.drawText(text)

    if image_paths:
        y = 400
        for img in image_paths[:3]:
            c.drawImage(img, 50, y, width=120, height=90)
            y -= 100

    c.showPage()
    c.save()

    if cover_path:
        merger = PdfMerger()
        merger.append(cover_path)
        merger.append(tmp_path)
        merger.write(output_path)
        merger.close()
        os.remove(tmp_path)
    else:
        os.rename(tmp_path, output_path)