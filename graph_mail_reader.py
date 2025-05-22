import os
import requests
from msal import ConfidentialClientApplication
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
TENANT_ID     = os.getenv("TENANT_ID")
CLIENT_ID     = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_EMAIL    = os.getenv("EMAIL_ADDRESS")

# MSAL setup
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE     = ["https://graph.microsoft.com/.default"]

app = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY
)

def get_access_token():
    """
    Acquire an access token using MSAL.
    """
    token_resp = app.acquire_token_silent(SCOPE, account=None) or \
                 app.acquire_token_for_client(scopes=SCOPE)
    access_token = token_resp.get("access_token")
    if not access_token:
        raise RuntimeError(f"Could not obtain access token: {token_resp.get('error_description')}")
    return access_token


def graph_mail_reader():
    """
    Fetch unread messages from the user's Inbox via Microsoft Graph API.
    Returns a list of message dicts, with an added 'full_body_text' field.
    """
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Prefer": 'outlook.body-type="text"'  # Request body as plain text
    }
    endpoint = (
        f"https://graph.microsoft.com/v1.0/users/{USER_EMAIL}"
        "/mailFolders/Inbox/messages"
        "?$filter=isRead eq false"
        "&$select=id,subject,from,body"
        "&$top=500"
    )
    resp = requests.get(endpoint, headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(f"Graph API error: {resp.status_code} {resp.text}")
    messages = resp.json().get("value", [])
    
    # Extract plain text body content for each message
    for message in messages:
        body_content_html = message.get("body", {}).get("content", "")
        # Parse HTML and get text
        soup = BeautifulSoup(body_content_html, 'html.parser')
        plain_text_body = soup.get_text(separator='\n', strip=True)
        message["full_body_text"] = plain_text_body # Store clean text
        
    return messages


if __name__ == "__main__":
    msgs = graph_mail_reader()
    print(f"Found {len(msgs)} unread message(s).")
    for msg in msgs:
        sender   = msg["from"]["emailAddress"]
        subject  = msg["subject"]
        full_body = msg.get("full_body_text", "").strip() # Use the new field
        print("──────────────────────────────")
        print(f"ID:      {msg['id']}")
        print(f"From:    {sender['name']} <{sender['address']}>")
        print(f"Subject: {subject}")
        print(f"Body:\\n{full_body}") # Print the full body
