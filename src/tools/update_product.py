from langchain_core.tools import tool
from repositories.productdb import product_db


@tool
def update_product(product_code: str, quantity: int) -> str:
    """
    Subtracts the purchased quantity from the available stock in products.json.
    Call this when a user selects a product to buy.

    Args:
        product_code: The product code of the item (e.g. GAD001).
        quantity: The number of units to subtract from the current stock.

    Returns:
        A confirmation message with the updated stock level, or an error message.
    """
    if quantity <= 0:
        return "Error: quantity must be a positive number."

    try:
        updated = product_db.subtract_quantity(product_code, quantity)
        return (
            f"Stock updated for [{updated.product_code}] {updated.name}. "
            f"Sold: {quantity}. Remaining stock: {updated.quantity}."
        )
    except ValueError as ex:
        return f"Error: {str(ex)}"
    except Exception as ex:
        return f"Error: Failed to update product — {str(ex)}"
