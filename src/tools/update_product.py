from langchain_core.tools import tool
from repositories.productdb import product_db


@tool
def update_product(product_code: str, quantity: int) -> dict:
    """
    Subtracts the purchased quantity from the available stock.
    Call this when a user confirms a product purchase.

    Args:
        product_code: The product code of the item (e.g. ELC006).
        quantity:     The number of units purchased.

    Returns:
        {"product_code": ..., "name": ..., "sold": ..., "remaining_stock": ...}
        or {"error": "..."}
    """
    if quantity <= 0:
        return {"error": "quantity must be a positive number"}

    try:
        updated = product_db.subtract_quantity(product_code, quantity)
        return {
            "product_code": updated.product_code,
            "name": updated.name,
            "sold": quantity,
            "remaining_stock": updated.quantity,
        }
    except ValueError as ex:
        return {"error": str(ex)}
    except Exception as ex:
        return {"error": str(ex)}
