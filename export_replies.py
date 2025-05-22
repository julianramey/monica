# export_replies.py

import json
from graph_mail_reader import graph_mail_reader
import os

def export_to_json(path="replies.json", limit=500):
    """
    Fetch up to `limit` unread messages and dump them to a JSON file.
    """
    msgs = graph_mail_reader()[:limit]  # take first 500
    # We only need the fields you care about—subject, from, snippet, id
    simple = [
        {
            "from":  m["from"]["emailAddress"]["address"],
            "subject": m.get("subject",""),
            "body": m.get("full_body_text","")
        }
        for m in msgs
    ]
    full_path = os.path.abspath(path)
    with open(path, "w") as f:
        json.dump(simple, f, indent=2)
    print(f"Exported {len(simple)} messages to {full_path}")
    

if __name__ == "__main__":
    export_to_json()


