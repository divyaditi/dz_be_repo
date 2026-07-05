import json
from pathlib import Path

import chromadb
from langchain_core.tools import tool
from sentence_transformers import SentenceTransformer

CHROMA_DB_PATH = str(Path(__file__).parent.parent / "chroma_db")
COLLECTION_NAME = "tool_embeddings"
MODEL_NAME = "BAAI/bge-base-en-v1.5"

_model = None
_collection = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        _collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection


@tool
def search_tool(query: str, n_results: int = 3) -> dict:
    """
    Searches the tool registry using semantic similarity to find the most
    relevant tools for the user's query.

    Use this tool when you are unsure which tool to call for a given user request.
    It returns the top matching tools with their names, descriptions, and parameters.

    Args:
        query:     The user's message or intent (e.g. "I want to cancel my order").
        n_results: Number of top matching tools to return (default 3).

    Returns:
        {
          "tool": "search_tool",
          "data": {
            "query": "...",
            "matches": [
              {
                "tool_id": "...",
                "tool_name": "...",
                "tool_description": "...",
                "input_parameters": [...],
                "parameter_descriptions": {...},
                "relevance_score": float
              }
            ]
          }
        }
    """
    if not query:
        return {"tool": "search_tool", "data": {"message": "query is required"}}

    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode(
        "Represent this sentence for searching relevant passages: " + query,
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    matches = []
    if results and results["metadatas"]:
        for i, metadata in enumerate(results["metadatas"][0]):
            distance = results["distances"][0][i] if results.get("distances") else None
            matches.append({
                "tool_id": metadata.get("tool_id"),
                "tool_name": metadata.get("tool_name"),
                "tool_description": metadata.get("tool_description"),
                "parameters": json.loads(metadata.get("parameters", "[]")),
                "parameter_descriptions": json.loads(metadata.get("parameter_descriptions", "{}")),
                "relevance_score": round(1 - distance, 4) if distance is not None else None,
            })

    return {
        "tool": "search_tool",
        "data": {
            "query": query,
            "matches": matches,
        },
    }
