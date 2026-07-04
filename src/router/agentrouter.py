from fastapi import APIRouter
from pydantic import BaseModel
from agent.ecommerce_agent import ecommerce_agent

router = APIRouter()


class AgentRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    response: str


@router.post("/agent/chat")
async def chat(request: AgentRequest) -> AgentResponse:
    result = ecommerce_agent(request.message)
    return AgentResponse(response=str(result))
