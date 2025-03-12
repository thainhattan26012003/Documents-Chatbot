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

# import os
# import gemini  # Giả sử bạn đã cài đặt và cấu hình SDK cho Gemini
# from pydantic import BaseModel
# from config import QDRANT_COLLECTION, vectordb_provider
# from vector_db import embed


# os.environ["GEMINI_API_KEY"]

# class ChatRequest(BaseModel):
#     question: str

# def generate_answer_from_llm(query: str, context: str) -> str:
#     # Xây dựng prompt một cách rõ ràng, chuyên nghiệp và định hướng trả lời chỉ dựa trên tài liệu
#     prompt = (
#         f"Question: {query}\n\n"
#         f"Document Context: {context}\n\n"
#         f"Professional Answer:"
#     )
#     response = gemini.ChatCompletion.create(
#         model="gemini",  # Đảm bảo sử dụng model của Gemini đã được định cấu hình
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     "You are a highly professional and detail-oriented assistant. "
#                     "Your role is to provide precise and factual answers based solely on the provided document content. "
#                     "If the document does not contain sufficient information to answer the question, please respond with 'I don't know.'"
#                 )
#             },
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=350
#     )
#     return (
#         response["choices"][0]["message"]["content"].strip()
#         if response.get("choices")
#         else "No valid answer generated."
#     )

# def rag_flow(question: str) -> str:
#     search_results = vectordb_provider.search_vector(QDRANT_COLLECTION, embed(question))
#     if not search_results:
#         return "No relevant context found."
#     context = " ".join([result.payload.get("content", "") for result in search_results])
#     try:
#         answer = generate_answer_from_llm(question, context)
#         return answer if answer else "No valid answer generated."
#     except Exception as e:
#         return f"Error during answer generation: {str(e)}"