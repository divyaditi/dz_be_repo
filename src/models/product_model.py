from typing import Optional
from pydantic import BaseModel


class Product(BaseModel):
    product_id: str
    product_name: str
    price: float
    stock_quantity: int
    category: str = ""
    created_at: str = ""
    updated_at: str = ""
    is_active: bool = True


class Status(BaseModel):
    status_id: str
    status_name: str
    is_active: bool = True


class Order(BaseModel):
    order_id: str
    user_id: str
    status_id: str
    payment_status_id: str = ""
    shipping_address: str = ""
    total_amount: float
    created_at: str = ""
    updated_at: str = ""
    is_active: bool = True


class OrderItem(BaseModel):
    order_item_id: str
    order_id: str
    product_id: str
    quantity: int
    price: float
