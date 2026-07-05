from langchain_core.tools import tool
from repositories.productdb import product_db


@tool
def cancel_order(order_id: str) -> str:
    """
    Cancels an existing order by order ID.
    Only orders that are not already cancelled or delivered can be cancelled.
    If the user has already paid, the refund amount and timeline are included
    in the response so the agent can inform the user.

    Args:
        order_id: The unique ID of the order to cancel (e.g. ORD002).

    Returns:
        A confirmation message. If payment was made, includes the refund amount
        and a note that it will be refunded in 3-7 business days.
    """
    if not order_id:
        return "Error: order_id is required."

    try:
        order = product_db.cancel_order(order_id)

        if order.payment_status == "Paid":
            return (
                f"Order '{order.order_id}' for '{order.product_name}' has been successfully cancelled. "
                f"A refund of ₹{order.total:.2f} will be credited back to your original payment method "
                f"within 3-7 business days."
            )

        return (
            f"Order '{order.order_id}' for '{order.product_name}' has been successfully cancelled. "
            f"No payment was made, so no refund is applicable."
        )

    except ValueError as ex:
        return f"Error: {str(ex)}"
    except Exception as ex:
        return f"Error: Failed to cancel order — {str(ex)}"
