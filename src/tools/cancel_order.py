from langchain_core.tools import tool
from repositories.productdb import product_db


@tool
def cancel_order(order_id: str) -> str:
    """
    Cancels an existing order by order ID.
    Only orders that are not already cancelled or delivered can be cancelled.
    Returns raw order data after cancellation. The agent composes the response.

    Args:
        order_id: The unique ID of the order to cancel (e.g. ORD002).

    Returns:
        Raw cancellation data including order_id, product_name, status,
        payment_status, and total. Agent uses this to form the user message.
    """
    if not order_id:
        return "Error: order_id is required."

    try:
        order = product_db.cancel_order(order_id)
        return {
            "order_id": order.order_id,
            "product_name": order.product_name,
            "status": "Cancelled",
            "payment_status": order.payment_status,
            "total": order.total,
        }
    except ValueError as ex:
        return f"Error: {str(ex)}"
    except Exception as ex:
        return f"Error: Failed to cancel order — {str(ex)}"
