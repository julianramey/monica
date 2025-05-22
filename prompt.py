import os
import json
# import openai # No longer need the top-level openai import like this for v1.x
from dotenv import load_dotenv
from openai import OpenAI # Import the OpenAI client

load_dotenv()

# Initialize the OpenAI client
# The client will automatically pick up the OPENAI_API_KEY from the environment
client = OpenAI()

# 1) pull your API key (client does this automatically from env)
# openai.api_key = os.getenv("OPENAI_API_KEY") # Not needed with new client
# if not openai.api_key: # Handled by client or will error on API call
#     raise RuntimeError("Set your OPENAI_API_KEY env var")

# 2) load your data
with open("replies.json", "r") as f:
    messages = json.load(f) # Load all messages

# Remove SAMPLE_SIZE and messages_sample = all_messages[:SAMPLE_SIZE] if they exist

# 3) craft system + user messages
system_msg = (
    "You are an expert Python engineer. Your task is to generate the complete contents of a Python script file named `filter.py`. "
    "This script will be used by an influencer named Fiona Frills to filter email replies. "
    "Fiona is selling a $28 info product and her goal is to identify replies she should personally respond to. "
    "She wants to be helpful, answer genuine questions about her product, and engage with potential customers. "
    "She is NOT looking to collaborate, pay for services, or give away free products."
)

user_prompt = (
    f"Based on the persona and goals described, generate the full Python code for `filter.py`. "
    "The script should analyze email messages (provided in a JSON array format below) and decide if Fiona should reply. "
    "The `filter.py` script must include:\n\n"
    "1. Imports for `re` and `json` (and any other standard Python libraries necessary).\n"
    "2. A comprehensive list of compiled regular expressions named `FILTER_PATTERNS`. These patterns should identify and help exclude emails such as:\n"
    "    - Out of office / vacation auto-replies (e.g., 'Out of Office', 'OOO', 'Away Until', 'On holiday', 'Currently out', 'will be back on').\n"
    "    - Standard automated replies (e.g., 'Thanks for your email', 'message received', 'auto-reply', 'automatic response').\n"
    "    - DMARC reports or similar technical/administrative emails (e.g., subjects starting with 'Report Domain').\n"
    "    - One-time passcodes or security alerts.\n"
    "    - Inquiries about Fiona paying for services, collaborations, or discussing rates/charges (e.g., 'I charge', 'my rate is', 'flat fee', 'how much do you pay', 'collaboration fee').\n"
    "    - Explicitly negative or uninterested replies (e.g., 'not interested', 'unsubscribe', 'remove me', 'stop emailing').\n"
    "    - Emails with overly aggressive or inappropriate language.\n"
    "3. A function `def should_reply(message: dict) -> tuple[bool, str]:`\n"
    "    - It takes a single email message dictionary as input. Each message dictionary will have `id`, `from`, `subject`, and `body` (containing the full, plain text email body) keys.\n"
    "    - It should check the `subject` and `body` of the message against `FILTER_PATTERNS`.\n"
    "    - It must return a tuple: `(True, \"REASON_TO_REPLY\")` if Fiona should reply, or `(False, \"REASON_TO_FILTER\")` if she should not. \n"
    "    - The second element of the tuple (the reason string) should be a concise explanation for the decision (e.g., 'Genuine question', 'Out of office', 'Discussing rates').\n"
    "4. A `if __name__ == '__main__':` block that demonstrates how to:\n"
    "    - Load messages from `replies.json` (assuming it's in the same directory).\n"
    "    - Iterate through each message.\n"
    "    - Call `should_reply()` for each message.\n"
    "    - Print the `id`, `subject`, and the decision (Reply/Filter) and reason for a representative sample of messages (e.g., the first 10-20 messages, and a few examples of filtered and not-filtered messages if possible).\n\n"
    "Prioritize accuracy in filtering. The goal is to help Fiona focus her time on meaningful interactions. "
    "The `body` field in the JSON data contains the plain text content of the email.\n\n"
    "JSON data representing the email messages:\n"
    f"{json.dumps(messages, indent=2)}"
)

# 4) call the API
print(f"Sending {len(messages)} messages to the OpenAI API.") # Use full 'messages', wording changed from 'sample'
print(f"Estimated characters in prompt (excluding replies.json): {len(system_msg) + len(user_prompt.split('JSON data representing the email messages:')[0])}")
print(f"Estimated characters in replies.json data: {len(json.dumps(messages, indent=2))}") # Use full 'messages', wording changed from 'sample'

resp = client.chat.completions.create( # Use the new client syntax
    model="o4-mini", 
    messages=[
        {"role": "system", "content": system_msg},
        {"role": "user",   "content": user_prompt}
    ],
    temperature=1 
)

# 5) write out the filter.py
code_content = resp.choices[0].message.content

# Clean up the response to ensure it's only Python code
if code_content.startswith("```python"):
    code_content = code_content[len("```python"):].strip()
if code_content.endswith("```"):
    code_content = code_content[:-len("```")].strip()

with open("filter.py", "w") as f:
    f.write(code_content)

print("✅ filter.py generated!")
