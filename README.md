
## ✨ Overview

**Finance AI Assistant** is a cloud-native, multi-user personal finance platform that leverages the power of Artificial Intelligence to make managing money completely frictionless. 

Instead of manually navigating through drop-downs to log an expense, simply tell the AI: *"Got 50k salary and spent 2k on shoes."* The AI will automatically parse the intent, categorize it, calculate the amounts, and log it to your secure ledger.

With a beautiful dashboard, deep analytics, and an integrated **Financial Advisor Chat**, gaining insights into your spending habits has never been easier.

## 🚀 Features

- **🧠 Natural Language Logging:** Type your expenses in plain English. The Gemini AI engine automatically extracts the amount, category, and transaction type.
- **💬 AI Financial Advisor:** Ask questions like *"How can I save more money?"* or *"What am I spending the most on?"* and get contextual, data-driven advice.
- **🔒 Secure Multi-User Auth:** Built with Supabase JWT authentication. Your financial data is completely isolated, private, and encrypted.
- **📊 Dynamic Analytics:** Beautiful, interactive charts (powered by Recharts) showing spending trends, income vs. expenses, and categorical breakdowns.
- **🔮 Spending Predictions:** The AI analyzes your historical data to predict your spending trajectory for the current month.
- **📱 Telegram Bot Integration:** Add expenses on the go directly via Telegram *(Currently undergoing multi-user refactoring)*.

## 💻 Tech Stack

### Frontend Client
- **Framework:** [Next.js](https://nextjs.org/) (React)
- **Styling:** Tailwind CSS & Framer Motion (for fluid UI animations)
- **Data Visualization:** Recharts
- **Auth Management:** `@supabase/supabase-js`

### Backend Server
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **AI Engine:** Google Gemini (`google-generativeai`)
- **Database ORM:** SQLAlchemy
- **Database & Auth:** [Supabase](https://supabase.com/) (PostgreSQL)

---

## 🏗 Project Architecture

```text
finance-ai-assistant/
├── backend/
│   ├── ai_engine.py      # Core Gemini API logic and prompt engineering
│   ├── crud.py           # Database operations with user isolation
│   ├── main.py           # FastAPI endpoints & JWT validation
│   ├── models.py         # SQLAlchemy Database Schema
│   └── bot.py            # Telegram Bot polling script
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx      # Main Dashboard & Login UI
│   │   ├── layout.tsx    # Root layout and global styles
│   │   └── globals.css   # Tailwind configuration
│   └── src/components/
│       └── AIChat.tsx    # Floating AI Advisor widget
└── .gitignore            # Security filters for environment variables
```

---

## 🛠 Getting Started

### Prerequisites
- Node.js (v18+)
- Python 3.9+
- A [Supabase](https://supabase.com/) Project
- A [Google AI Studio](https://aistudio.google.com/) API Key

### 1. Clone the Repository
```bash
git clone https://github.com/Asphane/Finance-AI-Assistant.git
cd Finance-AI-Assistant
```

### 2. Backend Setup
Navigate to the backend directory and install dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory with the following variables:
```env
# Google AI API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Telegram Integration (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Supabase PostgreSQL Pooler URL
DATABASE_URL=postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# Supabase Auth
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

Start the FastAPI development server:
```bash
fastapi dev main.py
```

### 3. Frontend Setup
Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
npm install
```

Create a `.env.local` file in the `frontend/` directory:
```env
NEXT_PUBLIC_SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=your_supabase_anon_key_here
```

Start the Next.js development server:
```bash
npm run dev
```

Open `http://localhost:3000` in your browser. Create an account, log in, and start tracking your finances!

---

## 🗺 Roadmap (Future Improvements)

- [ ] **Telegram Bot Refactoring:** Update the existing bot to support Supabase Multi-User Auth via chat-ID mapping.
- [ ] **Google OAuth Integration:** Set up full Google Cloud Console OAuth keys for 1-click login.
- [ ] **Receipt Scanning (OCR):** Leverage Gemini-2.5-Flash Vision to extract transaction data directly from photos of receipts.
- [ ] **Budget Alerts:** Hard caps for specific categories with automatic Telegram push notifications at 80% usage.
- [ ] **Recurring Subscriptions:** Cron jobs to automate monthly fixed expenses (Rent, Netflix, Spotify).
- [ ] **Multi-Currency Support:** Live exchange rate API integration for international travelers.
- [ ] **Data Export:** Download ledgers as CSV/Excel files for tax season.

---

<div align="center">
  <i>Built with ❤️ using AI, FastAPI, and Next.js</i>
</div>
```
