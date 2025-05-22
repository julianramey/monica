# draft_replies.py

from graph_mail_reader import graph_mail_reader  # our function that returns `data`
from gpt.generator import generate_reply

def main():
    # 1) Fetch unread messages from Graph
    unread = graph_mail_reader()  # returns a list of message dicts

    print(f"\nGenerating drafts for {len(unread)} messages…\n")
    for msg in unread:
        body_snippet = msg.get("bodyPreview") or ""
        draft = generate_reply(body_snippet)
        print("──────────────────────────────────────")
        print(f"To:      {msg['from']['emailAddress']['address']}")
        print(f"Subject: Re: {msg['subject']}")
        print("Draft Reply:")
        print(draft, "\n")

if __name__ == "__main__":
    main()
