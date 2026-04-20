from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models, schemas, crud
from database import engine, get_db

import os
from supabase import create_client, Client
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        user = supabase.auth.get_user(token)
        return user.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance AI Assistant API")

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Finance AI Assistant API"}

@app.post("/transactions/", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    transaction.user_id = user_id
    return crud.create_transaction(db=db, transaction=transaction)

@app.get("/transactions/", response_model=List[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    transactions = crud.get_transactions(db, user_id=user_id, skip=skip, limit=limit)
    return transactions

@app.delete("/transactions/{transaction_id}", response_model=schemas.Transaction)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    db_transaction = crud.delete_transaction(db, transaction_id=transaction_id, user_id=user_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@app.delete("/transactions/current-month/expenses")
def wipe_current_month_expenses(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    count = crud.delete_current_month_expenses(db, user_id=user_id)
    return {"message": f"Deleted {count} expenses"}

from fastapi import File, UploadFile
import services

@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    content = await file.read()
    transactions = services.process_csv_upload(db, content)
    return {"message": f"Successfully processed {len(transactions)} transactions."}

import ai_engine

@app.get("/predict/")
def predict_spending(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    prediction = ai_engine.predict_next_month_spending(db, user_id=user_id)
    return prediction

from pydantic import BaseModel

class QuickAddRequest(BaseModel):
    text: str

from typing import List

@app.post("/transactions/quick-add/", response_model=List[schemas.Transaction])
def quick_add_transaction(req: QuickAddRequest, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    try:
        parsed_data_list = ai_engine.parse_natural_language_transaction(req.text)
        if not isinstance(parsed_data_list, list):
            parsed_data_list = [parsed_data_list] # Fallback just in case
            
        saved_transactions = []
        for parsed_data in parsed_data_list:
            transaction_data = schemas.TransactionCreate(**parsed_data)
            transaction_data.user_id = user_id
            saved = crud.create_transaction(db=db, transaction=transaction_data)
            saved_transactions.append(saved)
        return saved_transactions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class ChatRequest(BaseModel):
    message: str

@app.post("/chat/")
def chat(req: ChatRequest, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    try:
        reply = ai_engine.chat_with_data(req.message, db, user_id=user_id)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




