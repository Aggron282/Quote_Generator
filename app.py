from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from utils.pricing import generate_ai_price_estimate
from utils.ai_quote import generate_quote_text
from utils.ai_quote import polish_msg
import os
import smtplib
from dotenv import load_dotenv
load_dotenv()
from email.message import EmailMessage


PASSWORD = os.getenv("SMTP_PASSWORD");

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL = os.getenv("SMTP_EMAIL");


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def send_email(to_email, subject, body):
    print(body);
   
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as emailer:
            emailer.starttls()
            emailer.login(EMAIL, PASSWORD)
            emailer.sendmail(EMAIL, to_email, f"Subject: {subject}\n\n{body}")
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
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
    
        job_details = (
        f"{small_panes} small panes, {medium_panes} medium panes, {large_panes} large panes, "
        f"{distance} miles from Scottsdale & Shea, "
        f"{'Urgent' if urgency else 'Standard'} job, Discounts: {', '.join(discounts)}, "
        f"Second-story windows: {second_story}, Screens: {screens}, "
        f"Notes: {job_notes}, Availability: {available_dates}"
        f"Phone: {phone}"
        f"Email: {email}"
        f"Name: {name}"
         )

        image_path = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        fallback_price = (
            small_panes * 3 +
            medium_panes * 5 +
            large_panes * 7 +
            max(0, distance - 20) * 5 +
            (20 if urgency else 0)
        )

        # Try AI estimate only if image is present
        if image_path:
            try:
                ai_price = generate_ai_price_estimate(image_path, job_details, fallback_price)
            except Exception as e:
                print(f"AI fallback triggered due to: {e}")
                ai_price = fallback_price
        else:
            ai_price = fallback_price

        original_price = round(max(ai_price, 25), 2);

        if 'review' in discounts:
            ai_price -= 20
        if 'recurring' in discounts:
            ai_price *= 0.85
        elif 'biweekly' in discounts:
            ai_price *= 0.90

        ai_price = round(max(ai_price, 25), 2)
        print(ai_price,original_price)
        quote_text = generate_quote_text(name, ai_price,job_details, address)

        return render_template('quote.html', name=name, quote=quote_text, original_price = original_price, half_price = ai_price /2 , price=ai_price, image=image_path)

    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    name = request.form['name']
    quote = request.form['quote']
    original_price = request.form['original_price']
    price = request.form['price']

    body = polish_msg(quote,original_price,price,name)

    send_email(
        to_email="marco@thewindowknight.com",
        subject=f"New Scheduled Quote from {name}",
        body=body
    )

    return render_template("confirmation.html", name=name)

if __name__ == '__main__':
    app.run(debug=True)

