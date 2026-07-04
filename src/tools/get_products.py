from strands import tool
from repositories.productdb import product_db


@tool
def show_products() -> str:
    """
    Queries the product database and returns all available gadgets
    with their product code, name, price, and available quantity.
    No arguments required.
    """
    products = product_db.get_all_products()

    if not products:
        return "No products are currently available."

    lines = ["Available Gadgets:\n"]
    lines.append(f"{'Code':<10} {'Product Name':<32} {'Price (₹)':>10} {'Qty':>6}")
    lines.append("-" * 62)

    for p in products:
        lines.append(
            f"{p.product_code:<10} {p.name:<32} {p.price:>10.2f} {p.quantity:>6}"
        )

    return "\n".join(lines)
