from sqlalchemy.orm import Session
import models, schemas

def get_transaction(db: Session, transaction_id: int, user_id: str):
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id, models.Transaction.user_id == user_id).first()

def get_transactions(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).filter(models.Transaction.user_id == user_id).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int, user_id: str):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id, models.Transaction.user_id == user_id).first()
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
        return db_transaction
    return None

from datetime import datetime

def delete_current_month_expenses(db: Session, user_id: str):
    current_month_str = datetime.now().strftime("%Y-%m")
    transactions = db.query(models.Transaction).filter(models.Transaction.type == 'expense', models.Transaction.user_id == user_id).all()
    count = 0
    for tx in transactions:
        if tx.date and tx.date.strftime("%Y-%m") == current_month_str:
            db.delete(tx)
            count += 1
    db.commit()
    return count
