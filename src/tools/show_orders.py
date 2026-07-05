from typing import Optional
from langchain_core.tools import tool
from repositories.productdb import product_db


@tool
def show_orders(
    user_id: str,
    product_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    last_ordered: bool = False,
) -> dict:
    """
    Retrieves customer orders. Can fetch all orders or filter by product name
    and/or date range. Supports fetching the last ordered item if specified.

    Args:
        user_id:      The unique ID of the user (required).
        product_name: (Optional) Filter orders by product name.
        start_date:   (Optional) Start date filter (YYYY-MM-DD).
        end_date:     (Optional) End date filter (YYYY-MM-DD).
        last_ordered: (Optional) If true, returns only the most recently ordered item.

    Returns:
        {"tool": "show_orders", "data": {"orders": [...]}}
    """
    if not user_id:
        return {"tool": "show_orders", "data": {"message": "user_id is required"}}

    orders = product_db.get_orders_by_user_id(
        user_id=user_id,
        product_name=product_name,
        start_date=start_date,
        end_date=end_date,
        last_ordered=last_ordered,
    )

    return {"tool": "show_orders", "data": {"orders": orders}}
