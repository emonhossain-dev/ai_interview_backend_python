import os
import httpx

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


async def get_ai_response(user_text: str, role: str):

    prompt = f"""
You are a professional AI interviewer.

Role: {role}

Candidate Answer:
{user_text}

Instructions:
- Ask follow-up interview question
- Be strict but polite
- Keep response short and professional
"""

    return await groq_generate(prompt)


async def groq_generate(prompt: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are an expert technical interviewer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GROQ_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            return f"Groq Error: {response.text}"

        data = response.json()
        return data["choices"][0]["message"]["content"]





async def get_ai_response_chat(user_text: str):
    prompt = f"""
You are a helpful AI assistant. Respond naturally like ChatGPT.

User:
{user_text}
"""

    return await groq_generate_chat(prompt)


async def groq_generate_chat(prompt: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are an expert assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GROQ_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            return f"Groq Error: {response.text}"

        data = response.json()
        return data["choices"][0]["message"]["content"]


#
# import os
# import httpx
#
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
#
#
# async def gemini_generate(prompt: str, system_instruction: str = "You are a helpful assistant.") -> str:
#     headers = {
#         "Content-Type": "application/json"
#     }
#
#     payload = {
#         "system_instruction": {
#             "parts": [{"text": system_instruction}]
#         },
#         "contents": [
#             {
#                 "role": "user",
#                 "parts": [{"text": prompt}]
#             }
#         ],
#         "generationConfig": {
#             "temperature": 0.7
#         }
#     }
#
#     url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
#
#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             url,
#             headers=headers,
#             json=payload,
#             timeout=30
#         )
#
#         if response.status_code != 200:
#             return f"Gemini Error: {response.text}"
#
#         data = response.json()
#         return data["candidates"][0]["content"]["parts"][0]["text"]
#
#
# async def get_ai_response(user_text: str, role: str) -> str:
#     prompt = f"""
# Role: {role}
#
# Candidate Answer:
# {user_text}
#
# Instructions:
# - Ask follow-up interview question
# - Be strict but polite
# - Keep response short and professional
# """
#
#     return await gemini_generate(
#         prompt=prompt,
#         system_instruction="You are a professional AI interviewer and expert technical interviewer."
#     )
#
#
# async def get_ai_response_chat(user_text: str) -> str:
#     return await gemini_generate(
#         prompt=user_text,
#         system_instruction="You are a helpful AI assistant. Respond naturally and helpfully."
#     )




# import os
# import httpx
#
# DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
# DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
#
#
# async def deepseek_generate(prompt: str, system_instruction: str = "You are a helpful assistant.") -> str:
#     headers = {
#         "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
#         "Content-Type": "application/json"
#     }
#
#     payload = {
#         "model": "deepseek-chat",
#         "messages": [
#             {"role": "system", "content": system_instruction},
#             {"role": "user", "content": prompt}
#         ],
#         "temperature": 0.7
#     }
#
#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             DEEPSEEK_URL,
#             headers=headers,
#             json=payload,
#             timeout=30
#         )
#
#         if response.status_code != 200:
#             return f"DeepSeek Error: {response.text}"
#
#         data = response.json()
#         return data["choices"][0]["message"]["content"]
#
#
# async def get_ai_response(user_text: str, role: str) -> str:
#     prompt = f"""
# Role: {role}
#
# Candidate Answer:
# {user_text}
#
# Instructions:
# - Ask follow-up interview question
# - Be strict but polite
# - Keep response short and professional
# """
#     return await deepseek_generate(prompt, "You are a professional AI interviewer.")
#
#
# async def get_ai_response_chat(user_text: str) -> str:
#     return await deepseek_generate(
#         user_text,
#         "You are a helpful AI assistant. Respond naturally."
#     )