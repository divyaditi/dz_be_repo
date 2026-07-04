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

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

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
