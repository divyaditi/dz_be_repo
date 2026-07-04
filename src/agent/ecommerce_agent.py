import logging
from strands import Agent
from strands.models.litellm import LiteLLMModel
from settings import settings
from tools.get_products import show_products
from tools.update_product import update_product
from tools.update_user_profile import update_user_profile

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a helpful e-commerce assistant. You can help users:
- Browse available products (product code, name, price)
- Update their profile details such as address and phone number

Always be polite and concise. When showing products, format them clearly.
"""

# Initialise the Groq model via LiteLLM
# model_id uses the "groq/" prefix so LiteLLM routes to Groq's API
model = LiteLLMModel(
    client_args={
        "api_key": settings.GROQ_API_KEY,
    },
    model_id=settings.GROQ_MODEL_ID,
    params={
        "max_tokens": 1024,
        "temperature": 0.7,
    },
)

# Instantiate the agent with both tools
ecommerce_agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[show_products, update_product, update_user_profile],
)
