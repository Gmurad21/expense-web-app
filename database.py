import os
import psycopg2
from datetime import datetime, timedelta

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    type TEXT,
    category TEXT,
    amount REAL,
    comment TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


def add_transaction(user_id, type_, category, amount, comment):
    cursor.execute("""
    INSERT INTO transactions (user_id, type, category, amount, comment)
    VALUES (%s, %s, %s, %s, %s)
    """, (user_id, type_, category, amount, comment))
    conn.commit()


def get_balance(user_id):
    cursor.execute("""
    SELECT 
        COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) -
        COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0)
    FROM transactions
    WHERE user_id=%s
    """, (user_id,))
    return cursor.fetchone()[0]


def clear_all_data(user_id):
    cursor.execute("DELETE FROM transactions WHERE user_id=%s", (user_id,))
    conn.commit()


def get_start_date(period):
    now = datetime.now()

    if period == "day":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        return now - timedelta(days=7)
    elif period == "year":
        return now - timedelta(days=365)
    else:
        return now - timedelta(days=30)


def get_summary(user_id, period="month"):
    start = get_start_date(period)

    cursor.execute("""
    SELECT type, SUM(amount)
    FROM transactions
    WHERE user_id=%s AND date >= %s
    GROUP BY type
    """, (user_id, start))

    rows = cursor.fetchall()

    income = 0
    expense = 0

    for type_, total in rows:
        if type_ == "income":
            income = total
        elif type_ == "expense":
            expense = total

    return income, expense, income - expense


def get_categories(user_id, period="month"):
    start = get_start_date(period)

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM transactions
    WHERE user_id=%s AND type='expense' AND date >= %s
    GROUP BY category
    ORDER BY SUM(amount) DESC
    """, (user_id, start))

    return cursor.fetchall()


def get_last_transactions(user_id, limit=10):
    cursor.execute("""
    SELECT type, category, amount, comment, date
    FROM transactions
    WHERE user_id=%s
    ORDER BY date DESC
    LIMIT %s
    """, (user_id, limit))

    return cursor.fetchall()