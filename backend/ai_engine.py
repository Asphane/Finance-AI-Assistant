import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from google import genai
import crud

load_dotenv()
def predict_next_month_spending(db: Session, user_id: str):
    transactions = crud.get_transactions(db, user_id=user_id, limit=10000)
    
    if not transactions:
        return {"predicted_spending": 0, "message": "Not enough data"}
        
    data = [{"date": t.date, "amount": t.amount, "type": t.type, "category": t.category} for t in transactions]
    df = pd.DataFrame(data)
    
    # Filter only expenses
    df = df[df['type'] == 'expense'].copy()
    
    # Ensure dates are datetime objects
    df['date'] = pd.to_datetime(df['date'])
    
    # Group by month and sum the amounts
    df['month'] = df['date'].dt.to_period('M')
    monthly_spending = df.groupby('month')['amount'].sum().reset_index()
    
    if len(monthly_spending) < 2:
        return {"predicted_spending": monthly_spending['amount'].sum() if not monthly_spending.empty else 0, "message": "Need more months for accurate prediction, returning current sum."}
        
    # Simple Moving Average for prediction
    # Or, simple linear regression
    # For vibe coding simplicity, we'll use an exponential moving average (EMA)
    # which gives more weight to recent months.
    
    monthly_spending['ema'] = monthly_spending['amount'].ewm(span=3, adjust=False).mean()
    predicted_next_month = monthly_spending['ema'].iloc[-1]
    
    # Also predict by category
    category_group = df.groupby(['category', 'month'])['amount'].sum().reset_index()
    predictions_by_category = {}
    for category in category_group['category'].unique():
        cat_data = category_group[category_group['category'] == category]
        cat_ema = cat_data['amount'].ewm(span=3, adjust=False).mean()
        predictions_by_category[category] = float(cat_ema.iloc[-1])
        
    return {
        "predicted_spending": float(predicted_next_month),
        "predictions_by_category": predictions_by_category,
        "message": "Prediction based on Exponential Moving Average"
    }

def get_llm_categorization(description: str):
    """
    Calls the Gemini API to categorize the transaction description.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found. Using basic fallback categorization.")
        # Fallback logic if no API key is provided
        desc = description.lower()
        if any(word in desc for word in ['uber', 'lyft', 'transit', 'gas']): return 'Transport'
        elif any(word in desc for word in ['starbucks', 'restaurant', 'food']): return 'Food & Dining'
        return 'Other'

    try:
        client = genai.Client(api_key=api_key)
        prompt = f"Categorize this bank statement item: '{description}' into one of the following exact categories: 'Food & Dining', 'Transport', 'Subscriptions', 'Housing', 'Shopping', 'Income', 'Groceries', or 'Other'. Reply with ONLY the category name."
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        category = response.text.strip()
        # Ensure it's a valid string, else fallback to Other
        if len(category) > 20:
            return 'Other'
        return category
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return 'Other'

import json
import re

def parse_natural_language_transaction(text: str):
    """
    Parses a natural language string into a structured transaction using Gemini.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing. Cannot parse text.")
        
    client = genai.Client(api_key=api_key)
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    You are a financial AI. A user just typed: "{text}"
    Today's date is {today}.
    Identify ALL distinct transactions in the user's message (e.g. "Got my salary of 50000 and spent 2000 on shoes" means two transactions: one income, one expense).
    Extract the transaction details and reply with ONLY a valid JSON ARRAY of objects matching this schema exactly (no markdown formatting, no code blocks):
    [
        {{
            "date": "YYYY-MM-DD",
            "description": "Short clear description",
            "amount": float (the absolute value, positive number),
            "category": "One of: Food & Dining, Transport, Subscriptions, Housing, Shopping, Income, Groceries, or Other",
            "type": "expense" or "income"
        }}
    ]
    IMPORTANT: Even if there is only one transaction, you must return it inside an array [].
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    res_text = response.text.strip()
    
    # Robustly extract JSON array block
    match = re.search(r'\[.*\]', res_text, re.DOTALL)
    if match:
        res_text = match.group(0)
        
    try:
        data = json.loads(res_text)
        return data
    except Exception as e:
        print(f"Failed to parse JSON from Gemini: {res_text}")
        raise ValueError("Could not parse the transaction.")

def chat_with_data(user_message: str, db: Session, user_id: str):
    transactions = crud.get_transactions(db, user_id=user_id, limit=100)
    history = "\\n".join([f"{t.date}: {t.description} - ₹{t.amount} ({t.category})" for t in transactions])
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Please add your Gemini API Key to chat with me!"
        
    client = genai.Client(api_key=api_key)
    prompt = f"""
    You are FinAI, a helpful and premium AI financial assistant. 
    Here are the user's recent transactions (in INR ₹):
    {history}
    
    The user says: "{user_message}"
    
    Respond helpfully, concisely, and use ₹ for currency. Keep it under 3 sentences.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text.strip()

