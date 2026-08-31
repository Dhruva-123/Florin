from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.config import (
    ADMIN_USER_EMAIL,
    DB_URL,
    SQL_DB_CREATION_QUERY_PATH,
    SQL_TABLE_CREATION_QUERY_PATH,
)

if not DB_URL:
    raise RuntimeError("DB_URL is not configured.")

engine = create_engine(DB_URL)


def initialize_database():
    queries = [SQL_DB_CREATION_QUERY_PATH, SQL_TABLE_CREATION_QUERY_PATH]
    with engine.connect() as connection:
        for query_path in queries:
            if not query_path:
                continue
            with open(query_path, "r", encoding="utf-8") as query_file:
                db_creation_query = query_file.read()
            statements = db_creation_query.split(";")
            for statement in statements:
                statement = statement.strip()
                if statement:
                    connection.execute(text(statement))


def ensure_admin_user():
    if not ADMIN_USER_EMAIL:
        return

    with engine.connect() as connection:
        query = text("""
            INSERT INTO Users (email, phone_no, balance)
            VALUES (:email, NULL, 0)
        """)
        try:
            connection.execute(query, {"email": ADMIN_USER_EMAIL})
            connection.commit()
            print("Admin created successfully.")
        except Exception as exc:  # pragma: no cover - startup robustness
            print(f"Error occurred while creating admin user: {exc}")
            connection.rollback()

def clear_database():
    from app.data_access.admin_queries import clear_all_tables

    clear_all_tables()


def fetch_trade_history():
    from app.data_access.admin_queries import get_trade_history

    trades = get_trade_history()
    trade_logs = []
    for trade in trades:
        trade_logs.append({
            "id": trade[0],
            "buyer_id": trade[1],
            "seller_id": trade[2],
            "stock_id": trade[3],
            "quantity": trade[4],
            "price": trade[5],
            "created_at": trade[6],
        })
    return {"logs": trade_logs}