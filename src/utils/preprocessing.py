"""
preprocessing.py
================
Loads tool descriptions from tool_descriptions.json, generates embeddings
using sentence-transformers, and stores them in ChromaDB.

Run this once to populate the vector store before starting the server:
    python utils/preprocessing.py
"""

import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

TOOL_DESCRIPTIONS_FILE = Path(__file__).parent.parent / "data" / "tool_descriptions.json"
CHROMA_DB_PATH = str(Path(__file__).parent.parent / "chroma_db")
COLLECTION_NAME = "tool_embeddings"
MODEL_NAME = "BAAI/bge-base-en-v1.5"


def build_tool_text(tool: dict) -> str:
    """Builds a rich text representation of a tool for embedding."""
    text = f"Tool Name: {tool['tool_name']}\n"
    text += f"Description:\n{tool['tool_description']}\n"
    text += "Parameters:\n"
    for param in tool["parameters"]:
        desc = tool["parameter_descriptions"].get(param, "")
        text += f"- {param}: {desc}\n"
    return text


def run_preprocessing():
    print("Loading tool descriptions...")
    with open(TOOL_DESCRIPTIONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    tools = data["tools"]
    print(f"Loaded {len(tools)} tools.")

    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Connecting to ChromaDB at: {CHROMA_DB_PATH}")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for tool in tools:
        tool_text = build_tool_text(tool)
        embedding = model.encode(tool_text, normalize_embeddings=True).tolist()

        ids.append(tool["tool_id"])
        embeddings.append(embedding)
        documents.append(tool_text)
        metadatas.append({
            "tool_id": tool["tool_id"],
            "tool_name": tool["tool_name"],
            "tool_description": tool["tool_description"],
            "parameters": json.dumps(tool["parameters"]),
            "parameter_descriptions": json.dumps(tool["parameter_descriptions"]),
        })

    # Upsert so re-running doesn't create duplicates
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"Successfully embedded and stored {len(ids)} tools in ChromaDB.")
    print("Collection:", COLLECTION_NAME)
    print("Tool IDs stored:", ids)


if __name__ == "__main__":
    run_preprocessing()
