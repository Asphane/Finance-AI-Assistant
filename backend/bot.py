import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import ai_engine
import crud
import schemas
from database import SessionLocal

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to FinAI! Send me any expense, e.g., 'I spent ₹400 on Uber' and I'll log it for you."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    processing_msg = await update.message.reply_text("🤖 Thinking...")
    
    try:
        # 1. Parse with Gemini
        parsed_data_list = ai_engine.parse_natural_language_transaction(text)
        if not isinstance(parsed_data_list, list):
            parsed_data_list = [parsed_data_list]
            
        # 2. Save to Database
        db = SessionLocal()
        try:
            response_msg = "✅ Saved successfully:\\n"
            for parsed_data in parsed_data_list:
                transaction_data = schemas.TransactionCreate(**parsed_data)
                crud.create_transaction(db=db, transaction=transaction_data)
                
                sign = "+" if parsed_data['type'] == 'income' else "-"
                response_msg += (
                    f"\\n📝 {parsed_data['description']}\\n"
                    f"💰 {sign}₹{parsed_data['amount']} ({parsed_data['category']})\\n"
                )
            await processing_msg.edit_text(response_msg)
        except Exception as db_e:
            await processing_msg.edit_text(f"❌ Database Error: {db_e}")
        finally:
            db.close()
            
    except Exception as e:
        await processing_msg.edit_text(f"❌ Could not understand that transaction. Please try again.\\nError: {e}")

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or "your_token_here" in token:
        print("Error: TELEGRAM_BOT_TOKEN is missing or invalid in .env")
        return

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 FinAI Telegram Bot is running... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
