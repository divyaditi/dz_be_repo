"""
Manual test script for update_product tool.
Run from the src directory:
    python test_update_product.py
"""

import json
import sys
from pathlib import Path

# Make sure src/ is on the path when running from repo root
sys.path.insert(0, str(Path(__file__).parent))

from repositories.productdb import product_db
from tools.update_product import update_product

DATA_FILE = Path(__file__).parent / "data" / "products.json"

# ── helpers ──────────────────────────────────────────────────────────────────

def read_quantity(product_code: str) -> int:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        if item["product_code"].upper() == product_code.upper():
            return item["quantity"]
    raise ValueError(f"Product {product_code} not found in file.")


def restore_quantity(product_code: str, original: int):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        if item["product_code"].upper() == product_code.upper():
            item["quantity"] = original
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def run(name: str, result: str, expect_pass: bool, condition: bool):
    status = "PASS" if condition == expect_pass else "FAIL"
    print(f"[{status}] {name}")
    print(f"       Result   : {result}")
    print()


# ── tests ─────────────────────────────────────────────────────────────────────

def test_valid_subtraction():
    code = "GAD001"
    qty_before = read_quantity(code)
    deduct = 5

    result = update_product(product_code=code, quantity=deduct)
    qty_after = read_quantity(code)

    passed = qty_after == qty_before - deduct
    run("Valid subtraction (GAD001, qty=5)", result, True, passed)

    # restore
    restore_quantity(code, qty_before)


def test_insufficient_stock():
    code = "GAD005"
    qty_before = read_quantity(code)

    result = update_product(product_code=code, quantity=9999)
    qty_after = read_quantity(code)

    passed = "Error" in result and qty_after == qty_before
    run("Insufficient stock (GAD005, qty=9999)", result, True, passed)


def test_invalid_product_code():
    result = update_product(product_code="INVALID999", quantity=1)

    passed = "Error" in result
    run("Invalid product code (INVALID999)", result, True, passed)


def test_zero_quantity():
    result = update_product(product_code="GAD001", quantity=0)

    passed = "Error" in result
    run("Zero quantity rejected (GAD001, qty=0)", result, True, passed)


def test_negative_quantity():
    result = update_product(product_code="GAD001", quantity=-3)

    passed = "Error" in result
    run("Negative quantity rejected (GAD001, qty=-3)", result, True, passed)


def test_case_insensitive_code():
    code = "gad002"
    qty_before = read_quantity("GAD002")

    result = update_product(product_code=code, quantity=2)
    qty_after = read_quantity("GAD002")

    passed = qty_after == qty_before - 2
    run("Case-insensitive product code (gad002)", result, True, passed)

    restore_quantity("GAD002", qty_before)


# ── run all ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  update_product — manual test run")
    print("=" * 60)
    print()

    test_valid_subtraction()
    test_insufficient_stock()
    test_invalid_product_code()
    test_zero_quantity()
    test_negative_quantity()
    test_case_insensitive_code()

    print("=" * 60)
    print("  Done.")
    print("=" * 60)
