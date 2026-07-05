import logging
import time
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
from fastapi.responses import JSONResponse
from router.loginrouter import router as login_router
from router.agentrouter import router as agent_router
from tools.search_product import search_product
from tools.create_order import create_order
from tools.show_orders import show_orders
from tools.cancel_order import cancel_order
from tools.refund_order import refund_order
from tools.update_user_profile import update_user_profile
from tools.search_tool import search_tool

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def run_tool_tests():
    print("\n" + "=" * 60)
    print("TOOL FUNCTION TESTS")
    print("=" * 60)

    # ── search_product ────────────────────────────────────────────
    print("\n[1] search_product() — all products")
    print(search_product.invoke({}))

    print("\n[2] search_product(product_name='Sony') — specific search")
    print(search_product.invoke({"product_name": "Sony"}))

    print("\n[3] search_product(product_name='nonexistent') — no match")
    print(search_product.invoke({"product_name": "nonexistent"}))

    # ── create_order ──────────────────────────────────────────────
    print("\n[4] create_order — valid order")
    print(create_order.invoke({"user_id": "USR001", "product_id": "ELC006", "quantity": 1}))

    print("\n[5] create_order — insufficient stock")
    print(create_order.invoke({"user_id": "USR001", "product_id": "ELC006", "quantity": 9999}))

    print("\n[6] create_order — invalid product")
    print(create_order.invoke({"user_id": "USR001", "product_id": "INVALID", "quantity": 1}))

    # ── show_orders ───────────────────────────────────────────────
    print("\n[7] show_orders — all orders for user")
    print(show_orders.invoke({"user_id": "USR001"}))

    print("\n[8] show_orders — filter by product name")
    print(show_orders.invoke({"user_id": "USR001", "product_name": "Sony"}))

    print("\n[9] show_orders — date range filter")
    print(show_orders.invoke({"user_id": "USR001", "start_date": "2026-06-01", "end_date": "2026-07-05"}))

    print("\n[10] show_orders — last ordered only")
    print(show_orders.invoke({"user_id": "USR001", "last_ordered": True}))

    # ── cancel_order ──────────────────────────────────────────────
    print("\n[11] cancel_order — by order_id (Paid)")
    print(cancel_order.invoke({"user_id": "USR001", "order_id": "ORD002"}))

    print("\n[12] cancel_order — already delivered")
    print(cancel_order.invoke({"user_id": "USR001", "order_id": "ORD001"}))

    print("\n[13] cancel_order — by product name")
    print(cancel_order.invoke({"user_id": "USR001", "product_name": "Logitech"}))

    # ── refund_order ──────────────────────────────────────────────
    print("\n[14] refund_order — by order_id")
    print(refund_order.invoke({"user_id": "USR001", "order_id": "ORD002"}))

    print("\n[15] refund_order — by product name, last ordered")
    print(refund_order.invoke({"user_id": "USR001", "product_name": "Sony", "last_ordered": True}))

    # ── update_user_profile ───────────────────────────────────────
    print("\n[16] update_user_profile — update address and phone")
    print(update_user_profile.invoke({"user_id": "USR001", "address": "New York", "phone_no": "9876543210"}))

    print("\n[17] update_user_profile — invalid user")
    print(update_user_profile.invoke({"user_id": "INVALID", "address": "London"}))

    # ── search_tool (embedding search) ────────────────────────────
    search_tool_results = []

    def run_search(query: str):
        result = search_tool.invoke({"query": query})
        search_tool_results.append({"query": query, "result": result})
        print(result)

    print("\n[18] search_tool — 'I want to cancel my order'")
    run_search("I want to cancel my order")

    print("\n[19] search_tool — 'show me wireless mice'")
    run_search("show me wireless mice")

    print("\n[20] search_tool — 'I need a refund for my keyboard'")
    run_search("I need a refund for my keyboard")

    print("\n[21] search_tool — 'place an order for headphones'")
    run_search("place an order for headphones")

    print("\n[22] search_tool — 'show me my recent orders'")
    run_search("show me my recent orders")

    # Save search_tool results to JSON
    import json
    from pathlib import Path
    output_file = Path(__file__).parent / "data" / "search_tool_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(search_tool_results, f, indent=2, ensure_ascii=False)
    print(f"\nSearch tool results saved to: {output_file}")

    print("\n" + "=" * 60)
    print("TOOL TESTS COMPLETE")
    print("=" * 60 + "\n")


run_tool_tests()

logger = logging.getLogger(__name__)

app = FastAPI(title="e-commerce-agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "PATCH"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logger(request: Request, call_next):
    try:
        start = time.time()

        response = await call_next(request)

        process_time = round(time.time() - start, 3)

        logger.info(
            "%s %s completed in %ss",
            request.method,
            request.url.path,
            process_time,
        )

        return response

    except Exception as ex:
        logger.exception("Unhandled exception occurred while processing request")
        raise


app.include_router(login_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
