from typing import Optional
from langchain_core.tools import tool
from repositories.productdb import product_db


@tool
def cancel_order(
    user_id: str,
    order_id: Optional[str] = None,
    product_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    last_ordered: bool = False,
) -> dict:
    """
    Cancels a specific order. Can identify the order by order_id, or search
    by product_name and/or date range. If the order cannot be confidently
    identified (multiple matches), returns hitl_required=true for human review.

    The response includes payment_status:
    - "Payment Paid"   → agent informs user about refund
    - "Payment Unpaid" → agent informs user no refund applicable

    Args:
        user_id:      The unique ID of the user (required).
        order_id:     (Optional) Direct order ID to cancel.
        product_name: (Optional) Product name to identify the order.
        start_date:   (Optional) Start date filter (YYYY-MM-DD).
        end_date:     (Optional) End date filter (YYYY-MM-DD).
        last_ordered: (Optional) If true, targets the most recent matching order.

    Returns:
        {"tool": "cancel_order", "data": {"order_id", "status", "payment_status", "total_amount"}}
        or {"tool": "cancel_order", "data": {"hitl_required": true, "orders": [...]}}
    """
    if not user_id:
        return {"tool": "cancel_order", "data": {"message": "user_id is required"}}

    # If order_id is directly provided — cancel immediately
    if order_id:
        try:
            result = product_db.cancel_order(order_id)
            return {"tool": "cancel_order", "data": result}
        except ValueError as ex:
            return {"tool": "cancel_order", "data": {"message": str(ex)}}
        except Exception as ex:
            return {"tool": "cancel_order", "data": {"message": str(ex)}}

    # No order_id — search by filters to identify the order
    orders = product_db.get_orders_by_user_id(
        user_id=user_id,
        product_name=product_name,
        start_date=start_date,
        end_date=end_date,
        last_ordered=last_ordered,
    )

    # Filter out already cancelled/delivered
    cancellable = [o for o in orders if o["status"] not in ("Cancelled", "Delivered")]

    if not cancellable:
        return {"tool": "cancel_order", "data": {"message": "No cancellable orders found matching the criteria."}}

    if len(cancellable) == 1:
        # Exactly one match — cancel it
        try:
            result = product_db.cancel_order(cancellable[0]["order_id"])
            return {"tool": "cancel_order", "data": result}
        except ValueError as ex:
            return {"tool": "cancel_order", "data": {"message": str(ex)}}

    # Multiple matches — HITL required
    return {
        "tool": "cancel_order",
        "data": {
            "hitl_required": True,
            "message": "Multiple orders found. Please confirm which order to cancel.",
            "orders": [
                {
                    "order_id": o["order_id"],
                    "status": o["status"],
                    "total_amount": o["total_amount"],
                    "created_at": o["created_at"],
                    "items": o["items"],
                }
                for o in cancellable
            ],
        },
    }
