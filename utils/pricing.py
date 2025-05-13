import openai
import os
import base64
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("AI_KEY")

def generate_ai_price_estimate(image_path, details, fallback_price=0):
   
    if not os.path.exists(image_path):
        return fallback_price

    # Encode image to base64
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    system_prompt = (
        "You're an expert in window cleaning pricing. "
        "Use the photo and job details to estimate a fair price based on industry standards. "
        "Target $60/hour. If job looks easy or fast (~20 minutes), factor in a $25 minimum including fuel. "
        "Add $5 per mile for every mile beyond 20 miles from Scottsdale & Shea. "
        "Only reply with a object of two numbers the original and then the discounted one — no currency symbols or text."
        
    )

    user_prompt = (
        f"Here are the job details: {details}. Consider difficulty, estimated time, and market rate."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]
            }
        ],
        max_tokens=20
    )

    # Parse the price safely
    text = response.choices[0].message['content'].strip()
    try:
        return round(float(text), 2)
    except ValueError:
        return fallback_price
