import re
import json
import sys

# Senders we never want to hit (from old utils/filters.py)
NO_REPLY_ADDRESSES = [
    "mailer-daemon@", "no-reply@", "noreply@",
    "do-not-reply@", "bounce@", "dmarcreport@",
]

# Patterns that indicate we should NOT reply, with reasons
FILTER_PATTERNS = [
    # Out‐of‐office / vacation
    (r'\bOut of Office\b', 'Out of office'),
    (r'\bOOO\b', 'Out of office'),
    (r'\bAway Until\b', 'Out of office'),
    (r'\bOn (vacation|holiday)\b', 'Out of office'),
    (r'\bCurrently out\b', 'Out of office'),
    (r'\bwill be back on\b', 'Out of office'),
    (r'away from the (office|desk)', 'Out of office'), # Added from old

    # Automated / generic replies
    (r'\bauto-?reply\b', 'Automated reply'),
    (r'\bautomatic response\b', 'Automated reply'),
    (r'\bmessage received\b', 'Automated reply'),
    (r'\bThanks for your email\b', 'Automated reply'),
    (r'\bYour email has been.*received\b', 'Automated reply'),
    (r'\bThank you for contacting\b', 'Automated reply'),
    (r'\bplease allow.*to respond\b', 'Automated reply'),
    (r'je vous remercie', 'Automated reply (French)'), # Added from old
    (r'hours of operation', 'Automated reply (Hours)'), # Added from old
    # (r'^on.*wrote:$['\n']+', 'Quoted reply only'), # Example for more specific quote check, needs testing

    # DMARC / technical reports
    (r'^\[?Preview\]?.*Report Domain:', 'DMARC report'),

    # One‐time passcodes / security alerts
    (r'\bone[- ]time passcode\b', 'Passcode message'),
    (r'\blogin passcode\b', 'Passcode message'),

    # Rate / fee / payment inquiries (enhanced from old and new)
    (r'\bI charge', 'Discussing rates'),
    (r'\bmy rate is', 'Discussing rates'),
    (r'\bflat rate', 'Discussing rates'),
    (r'\b(fee|price|charges?)s?\b', 'Discussing rates/fees'), # Combined fee/price/charge
    (r'\$\d+', 'Discussing specific price'), # Added for amounts like $500
    (r'\bcommission', 'Discussing rates'),
    (r'\bbudget', 'Discussing rates'),
    (r'\bpaid partnership', 'Discussing rates (paid by Fiona)'),

    # Collaboration pitches (where Fiona is asked to collab, not selling)
    (r'\bcollab(oration)?', 'Collaboration request'),
    (r'\bwork together', 'Collaboration request'),

    # Negative / unsubscribe
    (r'\bnot interested', 'Not interested'),
    (r'\bunsubscribe', 'Unsubscribe request'),
    (r'\bremove me', 'Unsubscribe request'),
    (r'\bstop emailing', 'Unsubscribe request'),

    # Inappropriate / aggressive
    (r'\bscam\b', 'Spam / scam'),
    (r'\bspam\b', 'Spam / scam'),
]

# Compile patterns for performance
COMPILED_FILTERS = [
    (re.compile(pattern, re.IGNORECASE), reason)
    for pattern, reason in FILTER_PATTERNS
]

def should_reply(message: dict) -> tuple[bool, str]:
    """
    Decide whether to reply to a message.
    Returns (True, reason) if we should reply,
    or (False, reason) if we should filter it out.
    """
    subject = message.get('subject', '')
    body = message.get('body', '') # Assumes this is the full plain text body
    sender = message.get('from', '').lower() # Get sender, ensure it's a string
    if isinstance(message.get('from'), dict):
        sender = message['from'].get('emailAddress', {}).get('address', '').lower()

    # 1. Check against no-reply senders
    for deny_addr in NO_REPLY_ADDRESSES:
        if deny_addr in sender:
            return False, 'Sender in deny list'

    # 2. Check for empty body (after sender check)
    if not body.strip():
        return False, 'Empty message body'

    # 3. Check combined subject and body against regex patterns
    text_to_check = subject + '\n' + body
    for pat, reason in COMPILED_FILTERS:
        if pat.search(text_to_check):
            return False, reason
            
    # If no filter patterns matched, it's likely a genuine inquiry
    return True, 'Genuine question'

if __name__ == '__main__':
    # Load messages from replies.json
    try:
        with open('replies.json', encoding='utf-8') as f:
            messages = json.load(f)
    except FileNotFoundError:
        print("Error: replies.json not found. Please run export_replies.py first.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from replies.json: {e}", file=sys.stderr)
        sys.exit(1)

    # Print header
    print(f"Processed from: replies.json")
    print("Msg#\tID\tSubject\tDecision\tReason")
    
    kept_count = 0
    filtered_count = 0

    # Process all messages or a sample (e.g., messages[:20] for sample)
    for idx, msg_data in enumerate(messages, start=1):
        msg_id = msg_data.get('id', f'N/A_{idx}')
        # Ensure subject is a string before replace
        subject_str = str(msg_data.get('subject', ''))
        subject_preview = subject_str.replace('\n', ' ')[:50] # Preview of subject
        
        reply_flag, reason = should_reply(msg_data)
        decision = 'Reply' if reply_flag else 'Filter'
        
        if reply_flag:
            kept_count += 1
        else:
            filtered_count += 1
            
        # Print results for all messages or a sample
        # For full log, remove this conditional print or adjust the number
        if idx <= 20 or (reply_flag and kept_count <=5) or (not reply_flag and filtered_count <=10): 
            print(f"{idx}\t{msg_id[:10]}...\t{subject_preview}...\t{decision}\t{reason}")
        elif idx == 21:
            print("... (further output condensed, showing summary at end) ...")

    print("\n--- Summary ---")
    print(f"Total messages processed: {len(messages)}")
    print(f"Messages to reply to:   {kept_count}")
    print(f"Messages filtered out:  {filtered_count}")