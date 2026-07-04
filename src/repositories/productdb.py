import json
import logging
from pathlib import Path
from typing import List, Optional

from models.product_model import Product

logger = logging.getLogger(__name__)

# Path to the persistent JSON file — resolved relative to this file's location
DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"


class ProductDatabase:

    def _read(self) -> List[dict]:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: List[dict]) -> None:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_all_products(self) -> List[Product]:
        try:
            return [Product(**item) for item in self._read()]
        except FileNotFoundError:
            logger.error("products.json not found at %s", DATA_FILE)
            raise Exception(f"Product data file not found: {DATA_FILE}")
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to load products: {str(ex)}")

    def get_product(self, product_code: str) -> Optional[Product]:
        try:
            for item in self._read():
                if item["product_code"].upper() == product_code.upper():
                    return Product(**item)
            return None
        except Exception as ex:
            logger.error("ProductDatabase error", exc_info=True)
            raise Exception(f"Failed to fetch product: {str(ex)}")

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


product_db = ProductDatabase()
