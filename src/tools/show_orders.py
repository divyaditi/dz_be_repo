from typing import Optional
from langchain_core.tools import tool
from repositories.productdb import product_db


@tool
def show_orders(user_id: str, order_id: Optional[str] = None) -> str:
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
        Mode 1: List of all orders for the user.
        Mode 2: Full detail of the selected order.
    """
    if not user_id:
        return "Error: user_id is required."

    # ── MODE 2: Particular order detail ──────────────────────────────────────
    if order_id:
        order = product_db.get_order_by_id(order_id)
        if not order:
            return (
                f"No order found with ID '{order_id}'. "
                "Please select a valid order ID from your orders list."
            )
        lines = ["Order Details:\n"]
        lines.append(f"{'Field':<16} Value")
        lines.append("-" * 44)
        lines.append(f"{'Order ID':<16} {order.order_id}")
        lines.append(f"{'Product':<16} {order.product_name}")
        lines.append(f"{'Product Code':<16} {order.product_code}")
        lines.append(f"{'Quantity':<16} {order.quantity}")
        lines.append(f"{'Price (₹)':<16} {order.price:.2f}")
        lines.append(f"{'Total (₹)':<16} {order.total:.2f}")
        lines.append(f"{'Status':<16} {order.status}")
        lines.append(f"{'Order Date':<16} {order.order_date}")
        return "\n".join(lines)

    # ── MODE 1: List all orders ───────────────────────────────────────────────
    orders = product_db.get_orders_by_user_id(user_id)

    if not orders:
        return f"No orders found for user '{user_id}'."

    lines = [f"Orders for User: {user_id}\n"]
    lines.append(f"{'Order ID':<10} {'Product Name':<32} {'Qty':>4} {'Total (₹)':>10} {'Status':<12} {'Date':<12}")
    lines.append("-" * 84)
    for o in orders:
        lines.append(
            f"{o.order_id:<10} {o.product_name:<32} {o.quantity:>4} {o.total:>10.2f} {o.status:<12} {o.order_date:<12}"
        )

    lines.append(
        "\nAsk the user which order they want details for, then call show_orders(user_id=..., order_id=<id>)."
    )

    return "\n".join(lines)
