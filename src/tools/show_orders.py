from typing import Optional
from langchain_core.tools import tool
from repositories.productdb import product_db


@tool
def show_orders(user_id: str, order_id: Optional[str] = None) -> dict:
    """
    Handles order retrieval in two modes:

    MODE 1 — List all orders (order_id NOT provided):
        Returns all orders for the given user_id.
        After showing the list, ask the user which order they want details for,
        then call Mode 2 with that order_id.

    MODE 2 — Particular order detail (order_id IS provided):
        Returns full detail of a specific order.
        Only call after user picks an order_id from the Mode 1 list.

    Args:
        user_id:  The unique ID of the user (required for both modes).
        order_id: The order ID for full detail (e.g. "ORD001"). Triggers Mode 2.

    Returns:
        Mode 1: {"orders": [...]}
        Mode 2: {"order": {...}}
        Error:  {"error": "..."}
    """
    if not user_id:
        return {"error": "user_id is required"}

    # ── MODE 2: Single order detail ───────────────────────────────────────────
    if order_id:
        order = product_db.get_order_by_id(order_id)
        if not order:
            return {"error": f"order_id '{order_id}' not found"}
        return {
            "order": {
                "order_id": order.order_id,
                "product_name": order.product_name,
                "product_code": order.product_code,
                "quantity": order.quantity,
                "price": order.price,
                "total": order.total,
                "status": order.status,
                "payment_status": order.payment_status,
                "order_date": order.order_date,
            }
        }

    # ── MODE 1: All orders ────────────────────────────────────────────────────
    orders = product_db.get_orders_by_user_id(user_id)

    if not orders:
        return {"orders": []}

    return {
        "orders": [
            {
                "order_id": o.order_id,
                "product_name": o.product_name,
                "quantity": o.quantity,
                "total": o.total,
                "status": o.status,
                "payment_status": o.payment_status,
                "order_date": o.order_date,
            }
            for o in orders
        ]
    }
