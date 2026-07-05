from typing import Optional
from langchain_core.tools import tool
from repositories.productdb import product_db


@tool
def refund_order(
    user_id: str,
    order_id: Optional[str] = None,
    product_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    last_ordered: bool = False,
) -> dict:
    """
    Initiates a refund for a specific order. Can identify the order by order_id,
    or search by product_name and/or date range. If the order cannot be
    confidently identified, returns hitl_required=true for human review.
    Only orders with payment_status "Payment Paid" are eligible for refund.

    Args:
        user_id:      The unique ID of the user (required).
        order_id:     (Optional) Direct order ID to refund.
        product_name: (Optional) Product name to identify the order.
        start_date:   (Optional) Start date filter (YYYY-MM-DD).
        end_date:     (Optional) End date filter (YYYY-MM-DD).
        last_ordered: (Optional) If true, targets the most recent matching order.

    Returns:
        {"tool": "refund_order", "data": {"order_id", "status", "refund_amount"}}
        or {"tool": "refund_order", "data": {"hitl_required": true, "orders": [...]}}
    """
    if not user_id:
        return {"tool": "refund_order", "data": {"message": "user_id is required"}}

    try:
        result = product_db.refund_order(
            user_id=user_id,
            order_id=order_id,
            product_name=product_name,
            start_date=start_date,
            end_date=end_date,
            last_ordered=last_ordered,
        )
        return {"tool": "refund_order", "data": result}
    except ValueError as ex:
        return {"tool": "refund_order", "data": {"message": str(ex)}}
    except Exception as ex:
        return {"tool": "refund_order", "data": {"message": str(ex)}}
