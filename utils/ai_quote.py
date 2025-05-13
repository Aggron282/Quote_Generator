import openai
import os
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("AI_KEY")

def generate_quote_text(client_name, price, details,address):
    prompt = f"""
    write an email from {client_name} to the marco@thewindowknight.com about scheduling a window cleaning and have 3 placeholders for additional notes and then also contact info and availbility, include  a summary {details}
    and {address} for the discounts and then at the bottom lay out the price {price} , {price / 2} and remove any * or any confusing signs to text"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message['content']


def polish_msg(quote,price,original_price,name):
 prompt = f"""
    Polish the following quote so that it is clear and structured in list form:

    1. Provide a summary of this quote: {quote}. Clearly state if it includes inside and outside window cleaning. Show:
    - Total: ${price}
    - Original total before discounts: ${original_price}
    - Price for outside or inside only: ${int(price) / 2}

    2. Parse and list the client's name, email, and phone number from the quote:
    - Name: {name}
    - Email: [Extract from quote or "Not specified"]
    - Phone: [Extract from quote or "Not specified"]

    3. Parse and clearly display the service address from the quote. If not found, state "Not specified".

    4. List any special notes from the quote. If none are found, say "Not specified".

    5. List all discounts applied. If there are no discounts, say "No discount applied".

    6. List the available service dates or time frames from the quote. If not found, say "Not specified".

    Do not include comments or placeholders — use "Not specified" where needed.
    """
    
 response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
 return response.choices[0].message['content']
