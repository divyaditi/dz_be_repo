from langchain_core.tools import tool
from repositories.productdb import product_db


@tool
def cancel_order(order_id: str) -> str:
    """
    Cancels an existing order by order ID.
    Only orders that are not already cancelled or delivered can be cancelled.

    Args:
        order_id: The unique ID of the order to cancel (e.g. ORD001).

    Returns:
        A confirmation message indicating the order was cancelled, or an error message.
    """
    if not order_id:
        return "Error: order_id is required."

    try:
        order = product_db.cancel_order(order_id)
        return (
            f"Order '{order.order_id}' for '{order.product_name}' has been successfully cancelled."
        )
    except ValueError as ex:
        return f"Error: {str(ex)}"
    except Exception as ex:
        return f"Error: Failed to cancel order — {str(ex)}"
