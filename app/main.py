from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from app.menu import get_menu, get_item_by_id
from app.order import create_order, get_order
from app.payment import process_payment
from app.ai_summary import generate_order_summary

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

app = FastAPI()


class OrderItem(BaseModel):
    item_id: int
    quantity: int = Field(ge=1)


class OrderBody(BaseModel):
    items: List[OrderItem]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.get("/menu")
def list_menu():
    return get_menu()


@app.get("/menu/{item_id}")
def retrieve_menu_item(item_id: int):
    item = get_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/order")
def place_order(body: OrderBody):
    try:
        order = create_order([item.model_dump() for item in body.items])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return order


@app.get("/frontend/index.html")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/summary/{order_id}")
def order_summary(order_id: str):
    order = get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"summary": generate_order_summary(order)}


@app.post("/payment")
def make_payment(body: dict):
    return process_payment(
        order_id=body.get("order_id", ""),
        amount=body.get("amount", 0),
        simulate_failure=body.get("simulate_failure", False),
    )
