# email_reader.py

import os
from imapclient import IMAPClient
import pyzmail
from dotenv import load_dotenv

# 1. Load .env variables
load_dotenv()
EMAIL    = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")

if not EMAIL or not PASSWORD:
    print("❌ Missing .env variables!")
    print("EMAIL_ADDRESS =", EMAIL)
    print("EMAIL_PASSWORD =", PASSWORD)
    exit(1)

# 2. IMAP server settings for Outlook
IMAP_SERVER = 'outlook.office365.com'
IMAP_PORT   = 993

def fetch_unread():
    print("🔌 Connecting to IMAP server…")
    with IMAPClient(IMAP_SERVER, port=IMAP_PORT, ssl=True) as client:
        client.login(EMAIL, PASSWORD)
        client.select_folder('INBOX')
        
        # 3. Search for UNSEEN (unread) messages
        uids = client.search(['UNSEEN'])
        print(f"Found {len(uids)} unread message(s).")
        
        # 4. Fetch and display each
        if not uids:
            return
        response = client.fetch(uids, ['RFC822'])
        for uid, data in response.items():
            msg = pyzmail.PyzMessage.factory(data[b'RFC822'])
            subject = msg.get_subject()
            from_   = msg.get_addresses('from')
            if msg.text_part:
                body = msg.text_part.get_payload().decode(msg.text_part.charset)
            else:
                body = "(no text part)"
            
            print("───────────────────────────────")
            print(f"UID: {uid}")
            print(f"From: {from_}")
            print(f"Subject: {subject}")
            print("Body:")
            print(body[:500] + ("…" if len(body) > 500 else ""))  # only show first 500 chars

if __name__ == "__main__":
    fetch_unread()
