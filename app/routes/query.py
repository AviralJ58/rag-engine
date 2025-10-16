from fastapi import APIRouter
from app.utils.llm import generate_response

router = APIRouter()

@router.post("/query")
async def query_endpoint(payload: dict):
    """Takes user query and returns LLM-generated output (no retrieval yet)."""
    user_input = payload.get("query", "")
    if not user_input:
        return {"error": "Query text missing"}
    
    messages = [{"role": "user", "content": user_input}]
    result = generate_response(messages)
    return {"response": result}
