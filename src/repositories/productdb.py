import json
import logging
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

from models.product_model import Product, Order, OrderItem, Status

logger = logging.getLogger(__name__)

PRODUCTS_FILE    = Path(__file__).parent.parent / "data" / "products.json"
ORDERS_FILE      = Path(__file__).parent.parent / "data" / "orders.json"
ORDER_ITEMS_FILE = Path(__file__).parent.parent / "data" / "order_items.json"
STATUS_FILE      = Path(__file__).parent.parent / "data" / "status.json"


class ProductDatabase:

    # ── helpers ───────────────────────────────────────────────────────────────

    def _read_products(self) -> List[dict]:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_products(self, data: List[dict]) -> None:
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _read_orders(self) -> List[dict]:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_orders(self, data: List[dict]) -> None:
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _read_order_items(self) -> List[dict]:
        with open(ORDER_ITEMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_order_items(self, data: List[dict]) -> None:
        with open(ORDER_ITEMS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _read_status(self) -> List[dict]:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _status_name(self, status_id: str) -> str:
        for s in self._read_status():
            if s["status_id"] == status_id:
                return s["status_name"]
        return status_id

    # ── products ──────────────────────────────────────────────────────────────

    def get_categories(self) -> List[str]:
        try:
            items = self._read_products()
            return sorted(set(
                i.get("category", "") for i in items
                if i.get("category") and i.get("is_active", True)
            ))
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to fetch categories: {str(ex)}")

    def get_product(self, product_id: str) -> Optional[Product]:
        try:
            for item in self._read_products():
                if item["product_id"].upper() == product_id.upper() and item.get("is_active", True):
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
            items = [i for i in self._read_products() if i.get("is_active", True)]
            items = sorted(items, key=lambda x: x.get("created_at", ""), reverse=True)
            if query:
                items = [i for i in items if query.lower() in i["product_name"].lower()]
            if category:
                items = [i for i in items if category.lower() in i.get("category", "").lower()]
            if max_price is not None:
                items = [i for i in items if i["price"] <= max_price]
            total = len(items)
            return [Product(**i) for i in items[offset: offset + limit]], total
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to search products: {str(ex)}")

    def subtract_quantity(self, product_id: str, quantity: int) -> Product:
        try:
            data = self._read_products()
            for item in data:
                if item["product_id"].upper() == product_id.upper():
                    if item["stock_quantity"] < quantity:
                        raise ValueError(
                            f"Insufficient stock. Requested {quantity}, available {item['stock_quantity']}."
                        )
                    item["stock_quantity"] -= quantity
                    self._write_products(data)
                    return Product(**item)
            raise ValueError(f"Product '{product_id}' not found.")
        except ValueError:
            raise
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to update product: {str(ex)}")

    # ── orders ────────────────────────────────────────────────────────────────

    def get_orders_by_user_id(
        self,
        user_id: str,
        product_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        last_ordered: bool = False,
    ) -> List[dict]:
        try:
            orders = [o for o in self._read_orders() if o["user_id"] == user_id and o.get("is_active", True)]
            items = self._read_order_items()
            products = {p["product_id"]: p for p in self._read_products()}

            result = []
            for order in orders:
                order_items = [i for i in items if i["order_id"] == order["order_id"]]
                if product_name:
                    match = any(
                        product_name.lower() in products.get(i["product_id"], {}).get("product_name", "").lower()
                        for i in order_items
                    )
                    if not match:
                        continue
                order_date = order.get("created_at", "")
                if start_date and order_date < start_date:
                    continue
                if end_date and order_date > end_date:
                    continue
                result.append({
                    "order_id": order["order_id"],
                    "status": self._status_name(order["status_id"]),
                    "payment_status": self._status_name(order.get("payment_status_id", "")),
                    "total_amount": order["total_amount"],
                    "shipping_address": order["shipping_address"],
                    "created_at": order["created_at"],
                    "items": [
                        {
                            "product_id": i["product_id"],
                            "product_name": products.get(i["product_id"], {}).get("product_name", ""),
                            "quantity": i["quantity"],
                            "price": i["price"],
                        }
                        for i in order_items
                    ],
                })
            if last_ordered and result:
                result = [max(result, key=lambda o: o["created_at"])]
            return result
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to fetch orders: {str(ex)}")

    def get_order_by_id(self, order_id: str) -> Optional[dict]:
        try:
            orders = self._read_orders()
            items = self._read_order_items()
            products = {p["product_id"]: p for p in self._read_products()}
            for order in orders:
                if order["order_id"].upper() == order_id.upper() and order.get("is_active", True):
                    order_items = [i for i in items if i["order_id"] == order["order_id"]]
                    return {
                        "order_id": order["order_id"],
                        "status": self._status_name(order["status_id"]),
                        "status_id": order["status_id"],
                        "payment_status": self._status_name(order.get("payment_status_id", "")),
                        "total_amount": order["total_amount"],
                        "shipping_address": order["shipping_address"],
                        "created_at": order["created_at"],
                        "items": [
                            {
                                "product_id": i["product_id"],
                                "product_name": products.get(i["product_id"], {}).get("product_name", ""),
                                "quantity": i["quantity"],
                                "price": i["price"],
                            }
                            for i in order_items
                        ],
                    }
            return None
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to fetch order: {str(ex)}")

    def create_order(self, user_id: str, product_id: str, quantity: int) -> dict:
        try:
            product = self.subtract_quantity(product_id, quantity)
            orders = self._read_orders()
            order_items = self._read_order_items()
            status_list = self._read_status()
            processing_id = next((s["status_id"] for s in status_list if s["status_name"] == "Processing"), "STS001")
            unpaid_id = next((s["status_id"] for s in status_list if s["status_name"] == "Payment Unpaid"), "STS006")
            new_order_id = f"ORD{str(len(orders) + 1).zfill(3)}"
            new_item_id = f"OI{str(len(order_items) + 1).zfill(3)}"
            total_amount = product.price * quantity
            today = date.today().isoformat()
            orders.append({
                "order_id": new_order_id,
                "user_id": user_id,
                "status_id": processing_id,
                "payment_status_id": unpaid_id,
                "shipping_address": "",
                "total_amount": total_amount,
                "created_at": today,
                "updated_at": today,
                "is_active": True,
            })
            order_items.append({
                "order_item_id": new_item_id,
                "order_id": new_order_id,
                "product_id": product_id,
                "quantity": quantity,
                "price": product.price,
            })
            self._write_orders(orders)
            self._write_order_items(order_items)
            return {
                "order_id": new_order_id,
                "product_id": product_id,
                "product_name": product.product_name,
                "quantity": quantity,
                "total_amount": total_amount,
                "status": "Processing",
            }
        except ValueError:
            raise
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to create order: {str(ex)}")

    def cancel_order(self, order_id: str) -> dict:
        try:
            data = self._read_orders()
            status_list = self._read_status()
            cancelled_id = next((s["status_id"] for s in status_list if s["status_name"] == "Cancelled"), None)
            delivered_id = next((s["status_id"] for s in status_list if s["status_name"] == "Delivered"), None)
            paid_id = next((s["status_id"] for s in status_list if s["status_name"] == "Payment Paid"), None)
            for item in data:
                if item["order_id"] == order_id:
                    if item["status_id"] == cancelled_id:
                        raise ValueError(f"Order '{order_id}' is already cancelled.")
                    if item["status_id"] == delivered_id:
                        raise ValueError(f"Order '{order_id}' has been delivered and cannot be cancelled.")
                    item["status_id"] = cancelled_id
                    self._write_orders(data)
                    return {
                        "order_id": item["order_id"],
                        "status": "Cancelled",
                        "payment_status": "Payment Paid" if item.get("payment_status_id") == paid_id else "Payment Unpaid",
                        "total_amount": item["total_amount"],
                    }
            raise ValueError(f"Order '{order_id}' not found.")
        except ValueError:
            raise
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to cancel order: {str(ex)}")

    def refund_order(
        self,
        user_id: str,
        order_id: Optional[str] = None,
        product_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        last_ordered: bool = False,
    ) -> dict:
        try:
            status_list = self._read_status()
            paid_id = next((s["status_id"] for s in status_list if s["status_name"] == "Payment Paid"), None)
            cancelled_id = next((s["status_id"] for s in status_list if s["status_name"] == "Cancelled"), None)
            if not order_id:
                orders = self.get_orders_by_user_id(
                    user_id=user_id,
                    product_name=product_name,
                    start_date=start_date,
                    end_date=end_date,
                    last_ordered=last_ordered,
                )
                refundable = [o for o in orders if o["payment_status"] == "Payment Paid"]
                if not refundable:
                    return {"message": "No paid orders found matching the criteria."}
                if len(refundable) > 1:
                    return {
                        "hitl_required": True,
                        "message": "Multiple paid orders found. Please confirm which order to refund.",
                        "orders": refundable,
                    }
                order_id = refundable[0]["order_id"]
            data = self._read_orders()
            for item in data:
                if item["order_id"] == order_id:
                    if item.get("payment_status_id") != paid_id:
                        raise ValueError(f"Order '{order_id}' has no payment to refund.")
                    item["status_id"] = cancelled_id
                    self._write_orders(data)
                    return {
                        "order_id": item["order_id"],
                        "status": "Refund Initiated",
                        "refund_amount": item["total_amount"],
                    }
            raise ValueError(f"Order '{order_id}' not found.")
        except ValueError:
            raise
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to refund order: {str(ex)}")


product_db = ProductDatabase()
