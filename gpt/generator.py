# gpt/generator.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load keys
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 2. Init new client
client = OpenAI(api_key=api_key)

# 3. Load your brand prompt
with open("gpt/prompts/system_prompt_template.txt", "r") as f:
    SYSTEM_PROMPT = f.read()

def generate_reply(email_body: str) -> str:
    """
    Uses the V1 openai-python client to draft a reply.
    """
    resp = client.chat.completions.create(
        model="gpt-4.1-nano",            # or "gpt-4.1-nano" if you have access
        messages=[
            {"role": "system",  "content": SYSTEM_PROMPT},
            {"role": "user",    "content": email_body}
        ],
        max_tokens=1000,
        temperature=0.8
    )
    # The new response structure puts content here:
    return resp.choices[0].message.content.strip()
