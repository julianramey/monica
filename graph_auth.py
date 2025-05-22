# graph_auth.py

import os
from msal import ConfidentialClientApplication
from dotenv import load_dotenv

# 1. Load env
load_dotenv()
CLIENT_ID     = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID     = os.getenv("TENANT_ID")

# 2. MSAL setup
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE     = ["https://graph.microsoft.com/.default"]  # Application permissions

app = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY
)

# 3. Acquire token
result = app.acquire_token_silent(SCOPE, account=None)
if not result:
    result = app.acquire_token_for_client(scopes=SCOPE)

if "access_token" in result:
    print("✅ Got token! Expires in", result["expires_in"], "seconds.")
else:
    print("❌ Token error:", result.get("error_description"))
