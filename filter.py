import re
import json
import sys

# Patterns that indicate we should NOT reply, with reasons
FILTER_PATTERNS = [
    # Out‐of‐office / vacation
    (r'\bOut of Office\b', 'Out of office'),
    (r'\bOOO\b', 'Out of office'),
    (r'\bAway Until\b', 'Out of office'),
    (r'\bOn (vacation|holiday)\b', 'Out of office'),
    (r'\bCurrently out\b', 'Out of office'),
    (r'\bwill be back on\b', 'Out of office'),
    # Automated / generic replies
    (r'\bauto-?reply\b', 'Automated reply'),
    (r'\bautomatic response\b', 'Automated reply'),
    (r'\bmessage received\b', 'Automated reply'),
    (r'\bThanks for your email\b', 'Automated reply'),
    (r'\bYour email has been.*received\b', 'Automated reply'),
    (r'\bThank you for contacting\b', 'Automated reply'),
    (r'\bplease allow.*to respond\b', 'Automated reply'),
    # DMARC / technical reports
    (r'^\[?Preview\]?.*Report Domain:', 'DMARC report'),
    # One‐time passcodes / security alerts
    (r'\bone[- ]time passcode\b', 'Passcode message'),
    (r'\blogin passcode\b', 'Passcode message'),
    # Rate / fee / payment inquiries
    (r'\bI charge\b', 'Discussing rates'),
    (r'\bmy rate is\b', 'Discussing rates'),
    (r'\bflat rate\b', 'Discussing rates'),
    (r'\bfee\b', 'Discussing rates'),
    (r'\bcommission\b', 'Discussing rates'),
    (r'\bbudget\b', 'Discussing rates'),
    (r'\bpaid partnership\b', 'Discussing rates'),
    # Collaboration pitches
    (r'\bcollab(oration)?\b', 'Collaboration request'),
    (r'\bwork together\b', 'Collaboration request'),
    # Negative / unsubscribe
    (r'\bnot interested\b', 'Not interested'),
    (r'\bunsubscribe\b', 'Unsubscribe request'),
    (r'\bremove me\b', 'Unsubscribe request'),
    (r'\bstop emailing\b', 'Unsubscribe request'),
    # Inappropriate / aggressive
    (r'\bscam\b', 'Spam / scam'),
    (r'\bspam\b', 'Spam / scam'),
]

# Compile patterns for performance
COMPILED_FILTERS = [
    (re.compile(pattern, re.IGNORECASE), reason)
    for pattern, reason in FILTER_PATTERNS
]

def should_reply(message):
    """
    Decide whether to reply to a message.
    Returns (True, reason) if we should reply,
    or (False, reason) if we should filter it out.
    """
    subject = message.get('subject', '')
    body = message.get('body', '')
    text = subject + '\n' + body
    for pat, reason in COMPILED_FILTERS:
        if pat.search(text):
            return False, reason
    # If no filter patterns matched, it's likely a genuine inquiry
    return True, 'Genuine question'

if __name__ == '__main__':
    # Load messages from replies.json
    try:
        with open('replies.json', encoding='utf-8') as f:
            messages = json.load(f)
    except FileNotFoundError:
        print("Error: replies.json not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e, file=sys.stderr)
        sys.exit(1)

    # Print header
    print("ID\tSubject\tDecision\tReason")
    # Show up to 20 messages
    for idx, msg in enumerate(messages[:20], start=1):
        # Some messages may not have an 'id' field
        msg_id = msg.get('id', f'<#{idx}>')
        subject = msg.get('subject', '').replace('\n', ' ')
        reply, reason = should_reply(msg)
        decision = 'Reply' if reply else 'Filter'
        print(f"{msg_id}\t{subject}\t{decision}\t{reason}")