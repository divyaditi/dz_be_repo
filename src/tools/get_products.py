from typing import Optional
from langchain_core.tools import tool
from repositories.productdb import product_db
from constants import PRODUCT_DEFAULT_LIMIT, PRODUCT_PAGE_SIZE


@tool
def get_products(
    fetch_categories: bool = False,
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    query: Optional[str] = None,
    product_id: Optional[str] = None,
    offset: int = 0,
) -> dict:
    """
    Handles all product retrieval in three flows:

    FLOW 1 — fetch_categories=True:
        Returns available product categories.
        Use this first before listing products. Then ask user for category and max budget.

    FLOW 2 — category/max_price/query provided (no product_id):
        Returns paginated product list sorted latest first (10 per page).
        - For browsing: always ask category + max price before calling.
        - For direct name search: use query= with the product name, skip asking category/price.
        After showing list, ask user to pick one, then use Flow 3.
        For next page: increment offset by PRODUCT_PAGE_SIZE.

    FLOW 3 — product_id provided:
        Returns full detail of a specific product.
        Only call after user picks a product_id from a Flow 2 list. Never guess the id.

    Args:
        fetch_categories: True to get category list (Flow 1).
        category:         Category filter (e.g. "Audio", "Gaming").
        max_price:        Maximum price filter in ₹.
        query:            Product name/keyword for direct search.
        product_id:       Product code for full detail (e.g. "ELC005"). Triggers Flow 3.
        offset:           Pagination offset (0, 10, 20 ...).

    Returns:
        Flow 1: {"categories": [...]}
        Flow 2: {"products": [...], "total": int, "offset": int, "has_more": bool}
        Flow 3: {"product": {...}}
        Error:  {"error": "..."}
    """

    # ── FLOW 1: Categories ────────────────────────────────────────────────────
    if fetch_categories:
        categories = product_db.get_categories()
        return {"categories": categories}

    # ── FLOW 3: Single product detail ─────────────────────────────────────────
    if product_id:
        product = product_db.get_product(product_id)
        if not product:
            return {"error": f"product_id '{product_id}' not found"}
        return {
            "product": {
                "product_id": product.product_code,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "quantity": product.quantity,
                "created_at": product.created_at,
            }
        }

    # ── FLOW 2: Search / list ─────────────────────────────────────────────────
    products, total = product_db.search_products(
        query=query,
        category=category,
        max_price=max_price,
        limit=PRODUCT_DEFAULT_LIMIT,
        offset=offset,
    )

    if not products:
        return {"products": [], "total": 0, "offset": offset, "has_more": False}

    return {
        "products": [
            {
                "product_id": p.product_code,
                "name": p.name,
                "category": p.category,
                "price": p.price,
                "quantity": p.quantity,
            }
            for p in products
        ],
        "total": total,
        "offset": offset,
        "has_more": (offset + len(products)) < total,
        "next_offset": offset + PRODUCT_PAGE_SIZE,
    }
