from pydantic import BaseModel


class Product(BaseModel):
    product_code: str
    name: str
    price: float
    quantity: int
