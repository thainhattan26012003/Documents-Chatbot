import openai
from pydantic import BaseModel
from service_config import QDRANT_COLLECTION, vectordb_provider
from vector_db import embed


class ChatRequest(BaseModel):
    question: str

# def generate_answer_from_llm(query: str, context: str) -> str:
#     prompt = f"Question: {query}\nContext: {context}\nAnswer:"
#     response = openai.ChatCompletion.create(
#         model="gpt-4o-mini",
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                          """ 1. Chỉ sử dụng thông tin trong phần "Ngữ cảnh".
#                             2. Trả lời không vượt quá 500 từ.
#                             3. Nếu thông tin không có trong ngữ cảnh, trả lời: "Tôi không rõ thông tin này."
#                             4. Luôn trình bày câu trả lời bằng tiếng Việt rõ ràng, dễ hiểu.
#                             5. Nếu câu trả lời có từ 2 ý trở lên, BẮT BUỘC phải xuống dòng và dùng dấu gạch đầu dòng (-) ở đầu mỗi ý để liệt kê giống như mẫu ở ví dụ phía dưới.
#                                         """)
#             },
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=350
#     )
#     return response["choices"][0]["message"]["content"].strip() if response["choices"] else "No valid answer generated."

def generate_answer_from_llm(query: str, context: str) -> str:
    prompt = f""" 
    Bạn cần trả lời câu hỏi dựa trên ngữ cảnh đã cho.
    
    **Yêu cầu định dạng:**
    - Dùng **Markdown** để hiển thị rõ ràng.
    - Nếu có nhiều ý, dùng dấu **-** để liệt kê.
    - Nếu có từ 2 nội dung trở lên, phân tách bằng **xuống dòng kép** để dễ đọc.
    - Nếu không có thông tin trong ngữ cảnh, trả lời: `"Tôi không rõ thông tin này."`
    
    **Câu hỏi:** {query}
    \n
    **Ngữ cảnh:** {context}
    \n
    
    **Câu trả lời:**
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là một trợ lý AI có nhiệm vụ trả lời bằng tiếng Việt theo format Markdown."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
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
# import google.generativeai as genai
# from pydantic import BaseModel
# from service_config import QDRANT_COLLECTION, vectordb_provider
# from vector_db import embed
# from dotenv import load_dotenv
# load_dotenv()

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# class ChatRequest(BaseModel):
#     question: str

# def generate_answer_from_gemini(query: str, context: str) -> str:
#     prompt = f"""
#     Bạn là chatbot trả lời các câu hỏi dựa vào nội dung công văn được cung cấp bên dưới.

#     Quy tắc khi trả lời:
#     1. Chỉ sử dụng thông tin trong phần "Ngữ cảnh".
#     2. Trả lời không vượt quá 500 từ.
#     3. Nếu thông tin không có trong ngữ cảnh, trả lời: "Tôi không rõ thông tin này."
#     4. Luôn trình bày câu trả lời bằng tiếng Việt rõ ràng, dễ hiểu.
#     5. Nếu câu trả lời có từ 2 ý trở lên, BẮT BUỘC phải xuống dòng và dùng dấu gạch đầu dòng (-) ở đầu mỗi ý để liệt kê giống như mẫu ở ví dụ phía dưới.

#     Ngữ cảnh:
#     {context}

#     Câu hỏi:
#     {query}

#     Câu trả lời của bạn (tuân thủ đúng cấu trúc gạch đầu dòng nếu có nhiều ý):
#     """
    
#     model = genai.GenerativeModel('gemini-1.5-pro-latest')
#     response = model.generate_content(prompt)

#     return response.text.strip() if response.text else "Không tạo được câu trả lời hợp lệ."

# def rag_flow(question: str) -> str:
#     # Hybrid search (Semantic + Keyword)
#     search_results = vectordb_provider.search_vector(QDRANT_COLLECTION, embed(question), limit=3)

#     if not search_results:
#         return "No relevant context found."

#     context = "\n\n".join([res.payload["content"] for res in search_results])

#     try:
#         answer = generate_answer_from_gemini(question, context)
#         return answer
#     except Exception as e:
#         return f"Error during answer generation: {str(e)}"
