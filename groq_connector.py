import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_groq_response(user_input):
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "misleading answer"
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        temperature=1,
        max_completion_tokens=8192,
        top_p=1,
        stream=False,
        stop=None
    )
    return completion.choices[0].message.content