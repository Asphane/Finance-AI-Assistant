import pandas as pd
from sqlalchemy.orm import Session
import models, schemas, crud
import io

import ai_engine

def process_csv_upload(db: Session, file_content: bytes):
    df = pd.read_csv(io.BytesIO(file_content))
    
    # Expected columns: date, description, amount
    
    created_transactions = []
    for _, row in df.iterrows():
        desc = str(row.get('description', ''))
        category = ai_engine.get_llm_categorization(desc)
            
        transaction_data = schemas.TransactionCreate(
            date=pd.to_datetime(row['date']).date(),
            description=str(row['description']),
            amount=float(row['amount']),
            category=category,
            type='expense' if float(row['amount']) < 0 else 'income'
        )
        db_transaction = crud.create_transaction(db, transaction_data)
        created_transactions.append(db_transaction)
        
    return created_transactions
