# Florin

A beginner-friendly stock market simulator designed to help users understand investing, order flow, portfolio management, and trading behavior in a safe virtual environment.

> Florin is a learning-focused simulation platform. It does not provide real stock ownership, real wealth exposure, or financial advice. All trading occurs using the fictional Florin currency.

## Goal and Vision

Florin exists to make financial learning practical and approachable.

Our core goal is to build a platform where users can:

- learn how stock markets function without real financial risk,
- practice buying and selling assets in a simulated environment,
- understand portfolio tracking and position management,
- explore the logic behind order books, execution, and market activity,
- create a foundation for future AI-driven market tools and analytics.

The broader vision is to evolve Florin into a full simulation ecosystem for trading education and experimentation — from beginner users and market practice to advanced AI agents, strategies, portfolio insights, and data-driven learning tools.

## ER Diagram

![ER Diagram for Florin](./ER%20Diagram%20for%20Florin.png)

## What Florin Does Today

The current backend includes the core features of a trading simulator:

- user registration and login with JWT-based authentication,
- protected portfolio access,
- buy and sell order placement,
- market data retrieval,
- admin endpoints for trade history and database cleanup,
- MySQL-backed persistence for users, orders, holdings, and records.

## Current Status

The project is in active development and already includes a working FastAPI backend structure with working authentication and trading endpoints. The system is functional for local simulation and testing, but it is still evolving toward a richer trading platform.

This means the app is currently a strong base for:

- learning market flows,
- testing API logic,
- expanding data models,
- introducing more realistic market behavior,
- preparing for future user-facing product features.

## Future Prospects

### 1. More realistic market simulation
- live-like order matching,
- bid/ask spread behavior,
- order prioritization rules,
- price movement based on simulated market events.

### 2. AI and agent-based trading
- AI market agents operating in the simulator,
- automated buying/selling strategies,
- challenge modes for beginner and advanced users,
- strategy comparison dashboards.

### 3. Portfolio analytics and learning tools
- P&L reporting,
- transaction history dashboards,
- performance summaries,
- risk analysis for simulated portfolios.

### 4. Social and competitive features
- leaderboards,
- trading contests,
- friends/groups,
- challenge-based learning tracks.

### 5. Frontend and user experience
- dashboard UI,
- trading screens,
- portfolio charts,
- market watchlists,
- mobile-friendly interfaces.

### 6. Data and research layer
- news correlation,
- price event feeds,
- historical market simulation data,
- educational insights and beginner guides.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- MySQL / mysql-connector-python
- JWT authentication via python-jose
- Passlib + bcrypt
- Pytest

## Project Structure

```text
Florin/
├── app/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── schemas.py
│   ├── data_access/
│   │   ├── admin_queries.py
│   │   ├── auth_queries.py
│   │   ├── market_queries.py
│   │   ├── order_queries.py
│   │   └── portfolio_queries.py
│   ├── routes/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── market.py
│   │   ├── news.py
│   │   ├── orders.py
│   │   └── portfolio.py
│   └── services/
├── SQL queries/
│   ├── Creating Database.sql
│   └── Script for table creation from ER diagram.sql
├── tests/
│   ├── conftest.py
│   ├── README.md
│   └── test_endpoints.py
├── pytest.ini
├── requirements.txt
├── readme.md
├── TESTING_GUIDE.md
├── System Architecture.md
├── Trade Excecution Sequence.md
├── ER Diagram for Florin.png
├── MIT License
└── .gitignore
```

## Prerequisites

Before running the app locally, make sure you have:

- Python 3.9+
- MySQL Server installed and running
- A valid local database for Florin
- A terminal or IDE with access to the project folder

## Local Setup

1. Clone the repository

```bash
git clone <repository-url>
cd Florin
```

2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory

```env
SECRET_KEY=your-super-secret-key
DB_URL=mysql+mysql-connector-python://root:password@localhost:3306/florin
SQL_DB_CREATION_QUERY=SQL queries/Creating Database.sql
SQL_TABLE_CREATION_QUERY=SQL queries/Script for table creation from ER diagram.sql
ADMIN_USER_EMAIL=admin@florin.com
ADMIN_USER_ID=admin
ADMIN_USER_PWD=admin_password
STARTING_BALANCE_FOR_A_NEW_USER=10000
```

5. Start the application

```bash
uvicorn app.app:app --reload
```

6. Open the API docs in a browser

```text
http://127.0.0.1:8000/docs
```

## API Overview

### Authentication

#### Register

```http
POST /register
```

```json
{
  "user_id": "demo_user",
  "email": "demo@example.com",
  "password": "securepassword"
}
```

#### Login

```http
POST /login
```

```json
{
  "email": "demo@example.com",
  "password": "securepassword"
}
```

### Market

```http
GET /market
```

### Portfolio

```http
GET /portfolio
Authorization: Bearer <token>
```

### Orders

```http
POST /buy
Authorization: Bearer <token>
```

```json
{
  "symbol": "AAPL",
  "quantity": 5,
  "price": 190.25
}
```

```http
POST /sell
Authorization: Bearer <token>
```

```json
{
  "symbol": "AAPL",
  "quantity": 2,
  "price": 195.00
}
```

### News and Admin Routes

```http
GET /news
GET /trade_history
DELETE /clear_database
```

## Testing

Run the test suite with:

```bash
pytest
```

Additional guidance and troubleshooting notes are available in [TESTING_GUIDE.md](TESTING_GUIDE.md).

## Final Note

Florin is a simulation-first trading platform built to teach, experiment, and grow. The project already demonstrates a strong backend foundation, and its long-term ambition is to become a richer, more intelligent market education ecosystem with deeper functionality, better realism, and broader user value.

## License

This project is licensed under the MIT License.
