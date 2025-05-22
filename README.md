# AI Email Agent for Microsoft Office

## 1. Project Overview

This project implements an AI-powered agent designed to manage email replies. The agent automatically fetches unread emails, filters them based on predefined criteria, drafts personalized replies for relevant messages using an AI language model, and sends these replies. The primary goal is to efficiently manage customer engagement, answer questions, and promote your needs, while filtering out administrative emails, auto-replies, and irrelevant inquiries.

## 2. Core Workflow

The agent operates on a scheduled basis:

1.  **Fetch Unread Emails**: Periodically retrieves new unread emails from your Microsoft Outlook inbox using the Microsoft Graph API.
2.  **Filter Messages**: Each fetched email is processed through a filtering system (`utils/filters.py`). This system uses a combination of sender deny lists, checks for empty bodies, and a comprehensive set of regular expressions to identify and exclude:
    *   Out-of-office notices and vacation auto-replies.
    *   Standard automated responses (e.g., "message received").
    *   Technical reports (e.g., DMARC reports).
    *   Emails from no-reply addresses.
    *   Inquiries about paying for services, collaborations where she is expected to pay, or discussions about rates.
    *   Explicitly negative or uninterested replies (e.g., "unsubscribe," "not interested").
    *   Basic spam or scam messages.
3.  **Enqueue Relevant Emails**: Emails that pass the filtering stage are added to a sending queue with a randomized delay (configurable, typically 1-6 hours) to simulate natural response times.
4.  **Draft AI Reply**: When an email is due for a reply, its content (full plain text body) is sent to an AI model (e.g., OpenAI's GPT series) along with a system prompt that defines your persona and goals. The AI model generates a draft reply.
5.  **Send Reply & Mark as Read**: The drafted reply is sent from your email address via the Microsoft Graph API. The original incoming email is then marked as read to prevent reprocessing.

## 3. Key Scripts & Their Roles

*   **`agent.py`**: The main orchestrator. Manages the scheduling of tasks (fetching, filtering, enqueuing, dispatching replies).
*   **`graph_mail_reader.py`**: Handles fetching unread emails from Microsoft Graph API. It also cleans the email body content, converting it to plain text using BeautifulSoup and storing it as `full_body_text`.
*   **`utils/filters.py`**: Contains the core filtering logic. The `should_reply(message)` function determines if an email should be replied to, returning a boolean decision and a reason. This script includes deny lists for sender addresses and a comprehensive set of regex patterns.
*   **`gpt/generator.py`**: Interfaces with the OpenAI API (or a similar AI model provider if `gpt/generator.py` is adapted).
*   **`graph_mail_sender.py`**: Sends the AI-drafted replies via Microsoft Graph API and marks the original messages as read.
*   **`export_replies.py`**: A utility script to fetch unread messages and save their relevant fields (including the full plain text body) to `replies.json`. This is useful for analysis, testing filters, or generating training data.
*   **`prompt.py`**: A utility script used during development to interact with an AI model to help generate the initial set of regex patterns for `filter.py`. (The refined and active filter logic is now in `utils/filters.py`).
*   **`graph_auth.py`**: A standalone script likely used for initial testing of Microsoft Graph API authentication. The core authentication logic is also present within the mail reader and sender scripts.
*   **`draft_replies.py`**: A simpler script that fetches unread emails and generates drafts without the advanced filtering, queuing, or scheduling of `agent.py`. Likely an earlier version or a utility for quick drafting.
*   **`email_reader.py`**: An alternative script for fetching emails using IMAP, not currently integrated into the main `agent.py` workflow.

## 4. Setup and Configuration

### 4.1. Prerequisites
*   Python 3.x
*   A Microsoft 365 account with an email address.
*   An Azure AD application registration with appropriate Mail permissions (e.g., `Mail.ReadWrite`, `Mail.Send`) for Microsoft Graph API access.
*   An OpenAI API key (or access to a similar AI model provider if `gpt/generator.py` is adapted).

### 4.2. Installation
1.  Clone the repository.
2.  Install Python dependencies. It's recommended to use a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\\Scripts\\activate`
    pip install -r requirements.txt 
    ```
    *(Note: A `requirements.txt` file should be created containing necessary packages like `requests`, `msal`, `beautifulsoup4`, `openai`, `schedule`, `python-dotenv`)*

### 4.3. Environment Variables
Create a `.env` file in the root directory of the project with the following variables:

```env
# For Microsoft Graph API
TENANT_ID=YOUR_AZURE_AD_TENANT_ID
CLIENT_ID=YOUR_AZURE_AD_APP_CLIENT_ID
CLIENT_SECRET=YOUR_AZURE_AD_APP_CLIENT_SECRET
EMAIL_ADDRESS=fiona.frills@example.com # The email address the agent will use

# For OpenAI API (or other AI model)
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

### 4.4. System Prompt for AI
Ensure the system prompt file used by `gpt/generator.py` is correctly set up at `gpt/prompts/influencer_insider.txt`. This file should define your persona, the product your selling, the desired tone, and any specific instructions for reply generation.

## 5. Running the Agent

To start the main email agent:
```bash
python3 agent.py
```
The agent will then run continuously, fetching and processing emails according to its schedule. You will see log messages in the terminal indicating its activity. Press `Ctrl+C` to stop the agent.

### Utility Scripts:
*   To export current unread emails to `replies.json` for inspection or testing:
    ```bash
    python3 export_replies.py
    ```
*   To test the filtering logic directly on `replies.json`:
    ```bash
    python3 utils/filters.py 
    ```
    (This assumes `utils/filters.py` has its `if __name__ == '__main__':` block configured to process `replies.json`.)

## 6. Key Configuration Points

*   **Agent Scheduling & Delays (`agent.py`):**
    *   `MIN_DELAY`, `MAX_DELAY`: Control the randomized delay before sending a reply.
    *   `START_HOUR`, `END_HOUR`: Define the time window (PST) during which replies are dispatched.
    *   Schedule frequencies (e.g., `schedule.every().hour.do(enqueue_replies)`).
*   **AI Model (`gpt/generator.py`):**
    *   `model`: Specifies the AI model used (e.g., "gpt-4.1-nano", "o4-mini", "gpt-4-turbo").
    *   `max_tokens`, `temperature`: Parameters for the AI model completion.
*   **Filtering Rules (`utils/filters.py`):**
    *   `NO_REPLY_ADDRESSES`: List of sender email addresses/domains to always ignore.
    *   `FILTER_PATTERNS`: The core list of regex patterns and their corresponding reasons for filtering. This is the primary place to refine what gets filtered.
*   **Email Scope (`graph_mail_reader.py`):**
    *   The Graph API query currently targets unread messages in the Inbox (`?$filter=isRead eq false`). This can be adjusted if needed.

## 7. Important Considerations

*   **Microsoft Graph API Permissions**: Ensure the Azure AD application has the correct and least-privilege permissions required. Application permissions are typically needed for a background agent.
*   **Token Management**: The scripts handle MSAL token acquisition. Monitor for any persistent token errors.
*   **Cost Management**: API calls to AI models (like OpenAI) incur costs. The filtering step is crucial to minimize unnecessary calls. Monitor your API usage.
*   **Testing**: Thoroughly test the agent in a controlled environment before letting it manage live email communications. Review filtered messages and drafted replies carefully.
*   **Error Handling**: The scripts include some basic error handling, but further enhancements might be needed for a production-robust system.
*   **Idempotency**: The `mark_as_read` function helps prevent reprocessing emails, which is important.

This README should provide a good overview for anyone working on or trying to understand the project. 
