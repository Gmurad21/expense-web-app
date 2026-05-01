from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import database as db

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/add_income")
def add_income(
    user_id: int = Form(...),
    amount: float = Form(...),
    comment: str = Form("")
):
    db.add_transaction(user_id, "income", "Доход", amount, comment)
    return {"status": "ok"}


@app.post("/add_expense")
def add_expense(
    user_id: int = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    comment: str = Form("")
):
    db.add_transaction(user_id, "expense", category, amount, comment)
    return {"status": "ok"}


@app.get("/balance")
def get_balance(user_id: int):
    return {"balance": db.get_balance(user_id)}


@app.get("/dashboard")
def dashboard(user_id: int, period: str = "month"):
    income, expense, balance = db.get_summary(user_id, period)
    categories = db.get_categories(user_id, period)
    transactions = db.get_last_transactions(user_id)

    return {
        "income": income,
        "expense": expense,
        "balance": balance,
        "categories": categories,
        "transactions": transactions
    }


@app.post("/clear")
def clear(user_id: int = Form(...)):
    db.clear_all_data(user_id)
    return {"status": "cleared"}