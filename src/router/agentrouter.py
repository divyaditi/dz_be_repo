from fastapi import APIRouter, Depends
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agent.ecommerce_agent import ecommerce_agent
from router.dependencies import verify_token

router = APIRouter()


class AgentRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    response: str


@router.post("/agent/chat")
async def chat(request: AgentRequest, user_email: str = Depends(verify_token)) -> AgentResponse:
    result = ecommerce_agent.invoke({"messages": [HumanMessage(content=request.message)]})
    # Last message in the conversation is the agent's final response
    response = result["messages"][-1].content
    return AgentResponse(response=response)
