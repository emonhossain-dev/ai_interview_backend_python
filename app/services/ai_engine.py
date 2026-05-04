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