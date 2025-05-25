from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from utils.pricing import generate_ai_price_estimate
from utils.ai_quote import generate_quote_text, polish_msg, classify_quote_quality
from utils.pdf_maker import generate_quote_pdf, generate_customer_pdf;
from utils.email_templates import render_customer_email, render_owner_email
from utils.emailer import send_html_email_with_attachment
from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL = os.getenv("SMTP_EMAIL")
PASSWORD = os.getenv("SMTP_PASSWORD")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # --- Form Inputs ---
        name = request.form['name']
        address = request.form['address']
        urgency = 'urgency' in request.form
        discounts = request.form.getlist('discounts')
        email = request.form['email']
        phone = request.form['phone']
        small_panes = int(request.form.get('small_panes', 0))
        medium_panes = int(request.form.get('medium_panes', 0))
        large_panes = int(request.form.get('large_panes', 0))
        distance = float(request.form.get('distance', 0))
        job_notes = request.form.get('job_notes', '')
        available_dates = request.form.get('available_dates', '')
        second_story = request.form.get('second_story', '')
        screens = request.form.get('screens', '')

        if 'biweekly' in discounts and 'recurring' in discounts:
            discounts.remove('recurring')

        # --- Quote Details Summary ---
        job_details = (
            f"{small_panes} small panes, {medium_panes} medium panes, {large_panes} large panes, "
            f"{distance} miles from Scottsdale & Shea, "
            f"{'Urgent' if urgency else 'Standard'} job, Discounts: {', '.join(discounts)}, "
            f"Second-story windows: {second_story}, Screens: {screens}, "
            f"Notes: {job_notes}, Availability: {available_dates}, "
            f"Phone: {phone}, Email: {email}, Name: {name}"
        )

        # --- Handle Photos ---
        image_paths = []
        photos = request.files.getlist('photo')
        for photo in photos:
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(filepath)
                image_paths.append(filepath)

        # --- AI Price Estimate or Fallback ---
        fallback_price = (
            small_panes * 3 +
            medium_panes * 5 +
            large_panes * 7 +
            max(0, distance - 20) * 5 +
            (20 if urgency else 0)
        )
        image_path = image_paths[0] if image_paths else None
        if image_path:
            try:
                ai_price = generate_ai_price_estimate(image_path, job_details, fallback_price)
            except Exception as e:
                print(f"AI fallback triggered: {e}")
                ai_price = fallback_price
        else:
            ai_price = fallback_price

        # --- Apply Discounts ---
        original_price = round(max(ai_price, 25), 2)
        if 'review' in discounts:
            ai_price -= 20
        if 'recurring' in discounts:
            ai_price *= 0.85
        elif 'biweekly' in discounts:
            ai_price *= 0.90
        ai_price = round(max(ai_price, 25), 2)

        # --- AI Quality Classification ---
        quote_quality = classify_quote_quality(job_details, len(image_paths))

        # --- Generate PDF with Cover ---
        os.makedirs("pdfs", exist_ok=True)
        pdf_path = os.path.join("pdfs", f"{name.replace(' ', '_')}_quote.pdf")
        cover_path = f"static/pdfs/{quote_quality.lower().replace(' ', '_')}.pdf"
        pdf_path_ty = os.path.join("thank_you", f"{name.replace(' ', '_')}_thanks.pdf")
        cover_path_ty = f"static/pdfs/thanks.pdf"
        generate_quote_pdf(name, job_details, ai_price, original_price, quote_quality, image_paths, pdf_path, cover_path)
        generate_customer_pdf(name, job_details, image_paths, pdf_path_ty, cover_path_ty)

        # --- Send Emails ---
        send_html_email_with_attachment(
            to_email=email,
            subject="Thank You from The Window Knight!",
            html_body=render_customer_email(name),
            attachments=[pdf_path_ty]
        )

        send_html_email_with_attachment(
            to_email="marco@thewindowknight.com",
            subject=f"📬 New Quote from {name}",
            html_body=render_owner_email(name, email, quote_quality),
            attachments=[pdf_path] + image_paths
        )

        return render_template('confirmation.html')

    return render_template('index.html')


@app.route('/schedule', methods=['POST'])
def schedule():
    name = request.form['name']
    quote = request.form['quote']
    original_price = request.form['original_price']
    price = request.form['price']
    body = polish_msg(quote, original_price, price, name)

    
    send_html_email_with_attachment(
            to_email="marco@thewindowknight.com",
             subject=f"New Scheduled Quote from {name}",
            html_body=body,
            attachments=[]
        )

    return render_template("confirmation.html", name=name)


if __name__ == '__main__':
    app.run(debug=True)
