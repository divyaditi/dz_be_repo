from pydantic import BaseModel


class Product(BaseModel):
    product_code: str
    name: str
    price: float
    quantity: int
    category: str = ""
    created_at: str = ""


class Order(BaseModel):
    order_id: str
    user_id: str
    product_code: str
    product_name: str
    quantity: int
    price: float
    total: float
    status: str
    payment_status: str = "Unpaid"
    order_date: str
