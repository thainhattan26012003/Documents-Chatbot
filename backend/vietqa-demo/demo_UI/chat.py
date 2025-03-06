import openai
from pydantic import BaseModel
from config import QDRANT_COLLECTION, vectordb_provider
from vector_db import embed


class ChatRequest(BaseModel):
    question: str

def generate_answer_from_llm(query: str, context: str) -> str:
    prompt = f"Question: {query}\nContext: {context}\nAnswer:"
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a chatbot that only provides answers based on the information in the system. "
                    "If there is not enough information, respond with 'I don't know.'"
                )
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=350
    )
    return response["choices"][0]["message"]["content"].strip() if response["choices"] else "No valid answer generated."

def rag_flow(question: str) -> str:
    search_results = vectordb_provider.search_vector(QDRANT_COLLECTION, embed(question))
    if not search_results:
        return "No relevant context found."
    context = " ".join([result.payload.get("content", "") for result in search_results])
    try:
        answer = generate_answer_from_llm(question, context)
        return answer if answer else "No valid answer generated."
    except Exception as e:
        return f"Error during answer generation: {str(e)}"