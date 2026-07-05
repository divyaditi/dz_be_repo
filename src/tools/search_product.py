from typing import Optional
from langchain_core.tools import tool
from repositories.productdb import product_db
from constants import PRODUCT_DEFAULT_LIMIT, PRODUCT_PAGE_SIZE


@tool
def search_product(product_name: Optional[str] = None) -> dict:
    """
    Searches for products in the catalog.
    If product_name is provided, searches for specific products.
    If no product_name is provided, returns a list of all available products.

    Sample query: "Can you show me what wireless mice you have available?"

    Args:
        product_name: (Optional) Name of the product to search for.
                      If omitted, all products will be returned.

    Returns:
        {"tool": "search_product", "data": {"products": [...], "total": int, "has_more": bool}}
    """
    products, total = product_db.search_products(
        query=product_name,
        limit=PRODUCT_DEFAULT_LIMIT,
        offset=0,
    )

    return {
        "tool": "search_product",
        "data": {
            "products": [
                {
                    "product_id": p.product_id,
                    "product_name": p.product_name,
                    "category": p.category,
                    "price": p.price,
                    "stock_quantity": p.stock_quantity,
                    "created_at": p.created_at,
                }
                for p in products
            ],
            "total": total,
            "has_more": len(products) < total,
        },
    }
