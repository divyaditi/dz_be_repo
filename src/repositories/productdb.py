import json
import logging
from pathlib import Path
from typing import List, Optional, Tuple

from models.product_model import Product, Order

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"
ORDERS_FILE = Path(__file__).parent.parent / "data" / "orders.json"


class ProductDatabase:

    def _read(self) -> List[dict]:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: List[dict]) -> None:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_categories(self) -> List[str]:
        try:
            items = self._read()
            categories = sorted(set(i.get("category", "") for i in items if i.get("category")))
            return categories
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to fetch categories: {str(ex)}")

    def get_product(self, product_code: str) -> Optional[Product]:
        try:
            for item in self._read():
                if item["product_code"].upper() == product_code.upper():
                    return Product(**item)
            return None
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to fetch product: {str(ex)}")

    def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[List[Product], int]:
        try:
            items = self._read()

            # Always sort latest first
            items = sorted(items, key=lambda x: x.get("created_at", ""), reverse=True)

            # Filter by name/keyword query
            if query:
                items = [i for i in items if query.lower() in i["name"].lower()]

            # Filter by category
            if category:
                items = [i for i in items if category.lower() in i.get("category", "").lower()]

            # Filter by max price
            if max_price is not None:
                items = [i for i in items if i["price"] <= max_price]

            total = len(items)
            page = items[offset: offset + limit]

            return [Product(**i) for i in page], total
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to search products: {str(ex)}")

    def subtract_quantity(self, product_code: str, quantity: int) -> Product:
        try:
            data = self._read()
            for item in data:
                if item["product_code"].upper() == product_code.upper():
                    if item["quantity"] < quantity:
                        raise ValueError(
                            f"Insufficient stock. Requested {quantity}, "
                            f"available {item['quantity']}."
                        )
                    item["quantity"] -= quantity
                    self._write(data)
                    return Product(**item)
            raise ValueError(f"Product '{product_code}' not found.")
        except ValueError:
            raise
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to update product: {str(ex)}")

    def get_orders_by_user_id(self, user_id: str) -> List[Order]:
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Order(**item) for item in data if item["user_id"] == user_id]
        except FileNotFoundError:
            logger.error("orders.json not found at %s", ORDERS_FILE)
            raise Exception(f"Orders data file not found: {ORDERS_FILE}")
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to fetch orders: {str(ex)}")

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                if item["order_id"].upper() == order_id.upper():
                    return Order(**item)
            return None
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to fetch order: {str(ex)}")

    def cancel_order(self, order_id: str) -> Order:
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                if item["order_id"] == order_id:
                    if item["status"] == "Cancelled":
                        raise ValueError(f"Order '{order_id}' is already cancelled.")
                    if item["status"] == "Delivered":
                        raise ValueError(f"Order '{order_id}' has already been delivered and cannot be cancelled.")
                    item["status"] = "Cancelled"
                    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    return Order(**item)
            raise ValueError(f"Order '{order_id}' not found.")
        except ValueError:
            raise
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to cancel order: {str(ex)}")


product_db = ProductDatabase()
