import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MAX_QUESTIONS = 5

def build_system_prompt(category: str, topics: list, difficulty: str,
                         question_count: int) -> str:
    return f"""You are a professional interviewer conducting a Quick Practice Session.

Session Details:
- Category: {category}
- Topics: {", ".join(topics)}
- Difficulty: {difficulty}
- Current Question Number: {question_count}
- Total Questions: {MAX_QUESTIONS}

Your job:
1. Ask ONE clear interview question at a time based on the topics above.
2. After the candidate answers, give SHORT constructive feedback (2-3 sentences):
   - What was good about the answer
   - What could be improved
   - A quick tip
3. Keep questions relevant to the selected topics and difficulty level.
4. Be encouraging but honest.
5. After {MAX_QUESTIONS} questions total, give a final overall summary.

Format rules:
- When asking a question: start with "Q{question_count}:"
- When giving feedback: start with "✅ Feedback:"
- When giving final summary: start with "🎯 Session Complete!"
- Keep responses concise and clear.
- Do NOT ask multiple questions at once.
"""

def get_interview_response(messages: list, category: str, topics: list,
                            difficulty: str, question_count: int) -> str:
    system_prompt = build_system_prompt(category, topics, difficulty, question_count)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            *messages,
        ],
        max_tokens=1024,
    )
    return response.choices[0].message.content
