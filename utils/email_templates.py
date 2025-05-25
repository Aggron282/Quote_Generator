def render_owner_email(name, email, quote_quality):
    return f"""
    <div style="font-family: Arial; color:#003246;">
        <h2>📬 New Quote Received</h2>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Quality:</strong> {quote_quality}</p>
        <hr>
        <p>➡️ PDF attached for full details.</p>
    </div>
    """


def render_customer_email(name, discount_code="FIRST15"):
    return f"""
    <div style="font-family: Arial; color:#003246;">
        <h2>✨ Thank you for requesting a quote, {name}!</h2>
        <p>We're excited to clean your windows. See your attached quote PDF for details.</p>
        <div style="border:2px dashed #00e1ff; padding:20px; margin-top:20px; background:#f0fbff;">
            <h3 style="color:#0077b6;">🎉 15% OFF Your First Clean!</h3>
            <p style="font-size:18px;">Use code: <strong>{discount_code}</strong> when booking.</p>
        </div>
    </div>
    """
