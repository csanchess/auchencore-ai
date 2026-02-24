import os
from openai import OpenAI
from dotenv import load_dotenv
from prompts import AUCHENCORE_SYSTEM_PROMPT

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def stream_analysis(messages):

    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content