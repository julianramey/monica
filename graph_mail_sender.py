# graph_mail_sender.py

import os, requests
from graph_mail_reader import get_access_token, USER_EMAIL

def send_email(to_address: str, subject: str, body: str):
    """
    Uses Graph API to send an email and saves it to Sent Items.
    """
    token = get_access_token()
    url = f"https://graph.microsoft.com/v1.0/users/{USER_EMAIL}/sendMail"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json"
    }
    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "html",
                "content": body.replace("\n","<br>")
            },
            "toRecipients": [
                {"emailAddress": {"address": to_address}}
            ]
        },
        "saveToSentItems": "true"
    }
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()

def mark_as_read(message_id: str):
    """
    Flags the original message as read so we don't reply twice.
    """
    token = get_access_token()
    url = f"https://graph.microsoft.com/v1.0/users/{USER_EMAIL}/messages/{message_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json"
    }
    resp = requests.patch(url, headers=headers, json={"isRead": True})
    resp.raise_for_status()
