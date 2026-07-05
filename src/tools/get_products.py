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
) -> str:
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
        Flow 1: Category list.
        Flow 2: Paginated product list with product_id column.
        Flow 3: Full product detail.
    """

    # ── FLOW 1: Return available categories ──────────────────────────────────
    if fetch_categories:
        categories = product_db.get_categories()
        if not categories:
            return "No categories available."
        lines = ["Available Categories:\n"]
        for i, cat in enumerate(categories, 1):
            lines.append(f"  {i}. {cat}")
        lines.append("\nPlease select a category and share your maximum budget (₹) to see products.")
        return "\n".join(lines)

    # ── FLOW 3: Full detail for a selected product ────────────────────────────
    if product_id:
        product = product_db.get_product(product_id)
        if not product:
            return (
                f"No product found with code '{product_id}'. "
                "Please select a valid product code from the list."
            )
        lines = ["Product Details:\n"]
        lines.append(f"{'Field':<16} Value")
        lines.append("-" * 44)
        lines.append(f"{'Code':<16} {product.product_code}")
        lines.append(f"{'Name':<16} {product.name}")
        lines.append(f"{'Category':<16} {product.category}")
        lines.append(f"{'Price (₹)':<16} {product.price:.2f}")
        lines.append(f"{'In Stock':<16} {product.quantity} units")
        lines.append(f"{'Added On':<16} {product.created_at}")
        return "\n".join(lines)

    # ── FLOW 2 / SPECIAL: Search or list products ─────────────────────────────
    products, total = product_db.search_products(
        query=query,
        category=category,
        max_price=max_price,
        limit=PRODUCT_DEFAULT_LIMIT,
        offset=offset,
    )

    if not products:
        return "No products found matching your filters. Try a different category or budget."

    shown_from = offset + 1
    shown_to = offset + len(products)

    lines = [f"Products (showing {shown_from}–{shown_to} of {total}, latest first):\n"]
    lines.append(f"{'product_id':<10} {'Product Name':<36} {'Category':<24} {'Price (₹)':>10} {'Qty':>6}")
    lines.append("-" * 90)
    for p in products:
        lines.append(
            f"{p.product_code:<10} {p.name:<36} {p.category:<24} {p.price:>10.2f} {p.quantity:>6}"
        )

    if shown_to < total:
        lines.append(
            f"\n{total - shown_to} more product(s) available. "
            f"Call get_products with offset={offset + PRODUCT_PAGE_SIZE} to see the next page."
        )

    lines.append(
        "\nAsk the user which product they want, then call get_products(product_id=<code>) for full details."
    )

    return "\n".join(lines)
