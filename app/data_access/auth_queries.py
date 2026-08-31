from sqlalchemy import text

from app.database import engine


def get_user_by_email(email: str):
    with engine.connect() as connection:
        query = text("""
            SELECT id, hashed_pwd FROM Users WHERE email = :email;
        """)
        return connection.execute(query, {"email": email}).first()


def get_user_by_id(user_id: str):
    with engine.connect() as connection:
        query = text("""
            SELECT id FROM Users WHERE id = :user_id;
        """)
        return connection.execute(query, {"user_id": user_id}).scalar_one_or_none()


def user_exists_by_id(user_id: str):
    with engine.connect() as connection:
        query = text("""
            SELECT * FROM Users WHERE id = :user_id;
        """)
        return connection.execute(query, {"user_id": user_id}).scalar_one_or_none()


def user_exists_by_email(email: str):
    with engine.connect() as connection:
        query = text("""
            SELECT * FROM Users WHERE email = :email;
        """)
        return connection.execute(query, {"email": email}).scalar_one_or_none()


def create_user(hashed_password: str, email: str, balance):
    with engine.connect() as connection:
        query = text("""
            INSERT INTO Users(hashed_pwd, email, balance) VALUES(:hashed_pwd, :email, :balance);
        """)
        result = connection.execute(
            query,
            {
                "hashed_pwd": hashed_password,
                "email": email,
                "balance": balance,
            },
        )
        connection.commit()
        return result.lastrowid
