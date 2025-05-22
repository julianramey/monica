# agent.py

import time, random
import schedule
from graph_mail_reader import graph_mail_reader
from utils.filters import should_reply
from gpt.generator import generate_reply
from graph_mail_sender import send_email, mark_as_read

# --- CONFIG ---
MIN_DELAY = 1 * 3600    # 1 hour
MAX_DELAY = 6 * 3600    # 6 hours
START_HOUR = 7          # 7:00 AM PST
END_HOUR   = 24         # midnight PST

# In-memory queue: [(send_timestamp, msg_dict), ...]
queue = []

def enqueue_replies():
    raw_msgs = graph_mail_reader()  # unread messages
    
    processed_msgs_for_queue = []
    for m in raw_msgs:
        reply_flag, reason = should_reply(m)
        if reply_flag:
            processed_msgs_for_queue.append(m)
        else:
            print(f"Agent filtering: Message ID {m.get('id', 'N/A')} from {m.get('from',{}).get('emailAddress',{}).get('address','N/A')} due to: {reason}")
            # Mark as read if configured to do so for filtered messages
            # mark_as_read(m["id"]) # Uncomment if you want to mark filtered messages as read immediately
            
    for msg in processed_msgs_for_queue:
        send_at = time.time() + random.uniform(MIN_DELAY, MAX_DELAY)
        queue.append((send_at, msg))
        
    if processed_msgs_for_queue:
        print(f"Enqueued {len(processed_msgs_for_queue)} replies.")

def dispatch_queue():
    now = time.time()
    for send_at, msg in queue.copy():
        # Check time window (PST) and scheduled time
        local_hour = time.localtime(now).tm_hour
        if now >= send_at and START_HOUR <= local_hour < END_HOUR:
            # Use the full_body_text for generating the reply
            email_body_for_gpt = msg.get("full_body_text", msg.get("bodyPreview", "")) 
            draft = generate_reply(email_body_for_gpt)
            
            to_addr = msg["from"]["emailAddress"]["address"]
            # Ensure subject is a string before concatenation
            original_subject = str(msg.get("subject", ""))
            subj    = "Re: " + original_subject
            
            send_email(to_addr, subj, draft)
            mark_as_read(msg["id"])
            queue.remove((send_at, msg))
            print(f"Sent reply to {to_addr} at {time.strftime('%X')}")

# Schedule: fetch new replies every hour, dispatch every 5 minutes
schedule.every().hour.do(enqueue_replies)
schedule.every(5).minutes.do(dispatch_queue)

print("🤖 Agent started. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(1)
