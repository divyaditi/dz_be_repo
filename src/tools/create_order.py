from langchain_core.tools import tool
from repositories.productdb import product_db


@tool
def create_order(user_id: str, product_id: str, quantity: int) -> dict:
    """
    Creates a customer order for a specific product.
    Subtracts the purchased quantity from available stock.

    Args:
        user_id:    The unique ID of the customer placing the order.
        product_id: The product ID to order (e.g. "ELC006").
        quantity:   Number of units to order.

    Returns:
        {"tool": "create_order", "data": {"order_id", "product_id", "product_name", "quantity", "total_amount"}}
    """
    if not user_id:
        return {"tool": "create_order", "data": {"message": "user_id is required"}}
    if not product_id:
        return {"tool": "create_order", "data": {"message": "product_id is required"}}
    if quantity <= 0:
        return {"tool": "create_order", "data": {"message": "quantity must be a positive number"}}

    try:
        result = product_db.create_order(user_id=user_id, product_id=product_id, quantity=quantity)
        return {"tool": "create_order", "data": result}
    except ValueError as ex:
        return {"tool": "create_order", "data": {"message": str(ex)}}
    except Exception as ex:
        return {"tool": "create_order", "data": {"message": str(ex)}}
