💰 ExpenseTracker
ExpenseTracker is a personal finance web application that helps users track their expenses and income, visualize their financial activity, and receive AI-generated spending insights.

It supports budgeting by category, provides charts for financial visualization, and integrates with Groq API to offer smart recommendations.

🚀 Features
✅ User Authentication

Register, login, logout with secure password hashing

Session management using Flask-Login

✅ Expense & Income Tracking

Add, update, delete transactions

Categorize spending (Food, Rent, Transport, etc.)

Filter transactions by date, category, or type

✅ Budget Management

Set monthly budgets per category

Track spending vs. budget

Alerts when spending exceeds limits

✅ AI-Powered Financial Insights

Uses Groq API to analyze spending habits

Suggests savings & smarter budgeting

✅ Financial Visualization

Pie charts for category-wise spending

Bar/line charts for monthly trends

Budget vs. spending comparison

✅ Reports & Export

Generate printable summaries

Export transactions to CSV

✅ Responsive UI

Built with Bootstrap, Chart.js, and mobile-friendly layout

🛠️ Tech Stack
Backend: Python, Flask

Frontend: HTML, CSS, JavaScript, Bootstrap, Chart.js

Database: PostgreSQL (SQLAlchemy ORM)

AI Integration: Groq API for smart financial insights

Environment Management: python-dotenv

📸 Screens / Pages
Home Page: Overview + login/register

Dashboard: Income/expenses summary, charts

Add Expense/Income: Forms to record transactions

All Transactions: Filterable table with edit/delete

Budget Page: Setup & overview of spending limits

AI Insights: Smart recommendations & savings tips

Reports: Printable + CSV export

Profile: Change password, manage user info

📂 Project Structure
csharp
Copy
Edit
ExpenseTracker/
│
├── app/
│   ├── __init__.py         # App factory, DB & Login setup
│   ├── models.py           # User, Expense, Income, Category, Budget models
│   ├── auth_routes.py      # Register, Login, Logout
│   ├── dashboard_routes.py # Dashboard, Budget, Transactions, Insights
│   ├── templates/          # HTML templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── budget_overview.html
│   │   ├── add_budget.html
│   │   ├── add_expense.html
│   │   └── insights.html
│   ├── static/             # CSS, JS, Images
│
├── config.py               # Flask configuration
├── run.py                  # Entry point
├── requirements.txt        # Dependencies
├── .env                    # Environment variables
└── README.md               # Project Documentation
⚙️ Setup & Installation
1️⃣ Clone the repo

bash
Copy
Edit
git clone https://github.com/your-username/ExpenseTracker.git
cd ExpenseTracker
2️⃣ Create a virtual environment

bash
Copy
Edit
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
3️⃣ Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
4️⃣ Set up the database
Create a PostgreSQL database:

sql
Copy
Edit
CREATE DATABASE expense_tracker_db;
Update .env file:

ini
Copy
Edit
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/expense_tracker_db
GROQ_API_KEY=your_groq_api_key_here
Initialize the database:

python
Copy
Edit
from app import db, create_app
app = create_app()
with app.app_context():
    db.create_all()
5️⃣ Run the app

bash
Copy
Edit
python run.py
Open http://127.0.0.1:5000 in your browser.

🔑 Environment Variables
Variable	Purpose
SECRET_KEY	Flask session security key
DATABASE_URL	PostgreSQL connection string
GROQ_API_KEY	Groq API key for AI insights

🤖 AI Integration (Groq API)
Sends summarized financial data to Groq API

Receives spending analysis, category overuse detection, and budget optimization tips

Displays insights in Insights Page

Example response:

"You spent 30% more on Food than usual. Consider reducing dining out and increasing home-cooked meals to save ₹1500 next month."

📊 Data Visualization
Pie Chart → Spending by category

Bar Chart → Month-wise totals

Line Chart → Trends over time

Budget Progress Bar → Shows usage vs. limit

📤 Export Features
Export all transactions as CSV

Download monthly PDF report

Print-friendly summaries

🧩 Implementation Phases
✅ Phase 1: Flask setup & PostgreSQL config
✅ Phase 2: Authentication (Register/Login/Logout)
✅ Phase 3: Expense, Income & Budget Management
✅ Phase 4: Groq API Integration for AI insights
✅ Phase 5: Charts & Reports with Chart.js
✅ Phase 6: Final UI + Documentation

🏗️ Future Enhancements
📱 Progressive Web App (PWA) version

🔔 Email/SMS alerts for budget limits

🤝 Multi-user collaboration (family/shared budgets)

💳 Bank API integration for auto-fetching transactions

👥 Team & Collaboration
Karthik Vijay (Lead Developer)

Teammates can collaborate via GitHub branches & PRs

✅ Evaluation Criteria
Criteria	Weight
Technical Implementation	50%
Functionality	30%
Project Management & Docs	20%

📜 License
MIT License – free to use & modify.

Would you like me to also:

✅ Add screenshots / diagrams section?
✅ Or include sample Groq API response example inside the README?

