# Generic AI Email Assistant

This project provides a framework for an AI-powered email assistant that can automatically read, filter, and draft replies to incoming emails. It uses the Microsoft Graph API to interact with an Outlook/Microsoft 365 mailbox and a large language model (LLM) like OpenAI's GPT for generating replies.

The system is designed to be customizable, allowing users to define the AI's persona, objectives, and specific email filtering rules.

## Features

*   **Email Reading:** Fetches unread emails from a specified Microsoft 365 account.
*   **HTML to Text Conversion:** Converts HTML email bodies to clean plain text.
*   **Customizable Filtering:** Allows users to define rules (using regular expressions) to identify emails that should not receive an AI-generated reply (e.g., out-of-office, automated responses, spam, specific unwanted inquiries).
*   **Customizable AI Persona & Reply Logic:** Users can define the AI's persona, tone, objectives, and information to include/avoid via a system prompt template.
*   **Automated Reply Drafting:** Generates draft replies for emails that pass the filtering stage.
*   **Reply Sending (with delay):** Sends drafted replies after a configurable random delay to appear more human.
*   **Environment Variable Configuration:** Securely manages API keys and other sensitive settings.

## Project Workflow

1.  **Authentication:** `graph_auth.py` handles authentication with the Microsoft Graph API using OAuth 2.0 client credentials flow.
2.  **Email Fetching:** `graph_mail_reader.py` fetches unread emails, extracts relevant information (sender, subject, body), and converts the body to plain text using `BeautifulSoup`.
3.  **Data Export (Optional):** `export_replies.py` can save the processed email data (including full text body) to `replies.json`. This was used for initial development and can be adapted for logging or analysis.
4.  **Filtering:** `agent.py` uses `utils/filters.py` to apply a series of regular expression-based filters. The `should_reply` function determines if an email warrants a reply and provides a reason if not.
5.  **Reply Generation:** If an email should be replied to, `agent.py` calls `gpt/generator.py`.
    *   `gpt/generator.py` loads a customizable system prompt from `gpt/prompts/system_prompt_template.txt`.
    *   It then calls the configured LLM (e.g., OpenAI) with the system prompt and the email body to generate a reply.
6.  **Reply Sending:** `graph_mail_sender.py` (via `agent.py`) sends the generated reply from the configured email account.
7.  **Main Orchestration:** `agent.py` is the main script that orchestrates the entire process: fetching, filtering, generating, and sending replies. It includes logic for scheduling and delays.

## Core Components

*   **`agent.py`**: The main orchestrator. Runs the email processing and reply loop.
*   **`graph_auth.py`**: Handles Microsoft Graph API authentication.
*   **`graph_mail_reader.py`**: Reads emails from the Microsoft Graph API.
*   **`graph_mail_sender.py`**: Sends emails via the Microsoft Graph API.
*   **`utils/filters.py`**: Contains the `should_reply` function and customizable `FILTER_PATTERNS` to decide if an email needs a reply.
*   **`gpt/generator.py`**: Interfaces with the LLM (e.g., OpenAI) to generate replies based on a system prompt.
*   **`gpt/prompts/system_prompt_template.txt`**: A template file where users define the AI's persona, objectives, tone, and guidelines for generating replies. **This is the primary file to edit for customizing AI behavior.**
*   **`.env.example`**: A template for your environment variables file. Rename to `.env` and fill in your actual credentials.
*   **`email_reader.py` (Utility):** A simple utility to read and print the content of `replies.json`.
*   **`draft_replies.py` (Utility):** An older script for drafting replies, largely superseded by `agent.py` and `gpt/generator.py` for automated drafting, but could be adapted for manual review/bulk drafting.
*   **`prompt.py` (Developer Utility):** A script used during development to generate the initial `filter.py` logic using an LLM. Not part of the core agent runtime.
*   **`filter.py` (Obsolete):** An older version of the filtering logic. The current, more robust filtering is in `utils/filters.py`. This root `filter.py` can be safely deleted.

## Setup and Configuration

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure `requirements.txt` is up-to-date with all necessary packages: `requests`, `beautifulsoup4`, `python-dotenv`, `openai`)*

3.  **Configure Microsoft Azure AD Application:**
    *   Go to the Azure portal and register a new application.
    *   Note down your **Tenant ID**, **Client ID**.
    *   Create a **Client Secret** and note it down.
    *   Grant the following **Application permissions** (not Delegated) to your app for Microsoft Graph:
        *   `Mail.ReadWrite`
        *   `Mail.Send`
    *   Ensure you grant admin consent for these permissions in Azure AD.

4.  **Set Up Environment Variables:**
    *   Rename `.env.example` to `.env`.
    *   Open `.env` and fill in your Azure AD app details and your OpenAI API key:
        ```env
        # --- Microsoft Graph API ---
        TENANT_ID=YOUR_AZURE_AD_TENANT_ID_HERE
        CLIENT_ID=YOUR_AZURE_AD_APP_CLIENT_ID_HERE
        CLIENT_SECRET=YOUR_AZURE_AD_APP_CLIENT_SECRET_HERE
        EMAIL_ADDRESS=your_agent_email@example.com # The email the agent will use

        # --- OpenAI API ---
        OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE

        # --- Agent Configuration (Optional) ---
        # AI_MODEL_NAME="gpt-4-turbo"
        # MIN_REPLY_DELAY_HOURS=1
        # MAX_REPLY_DELAY_HOURS=6
        # AGENT_START_HOUR_PST=7
        # AGENT_END_HOUR_PST=23
        ```
    *   The `EMAIL_ADDRESS` is the Microsoft 365 email account this agent will monitor and send replies from.

5.  **Customize AI Behavior:**
    *   Edit `gpt/prompts/system_prompt_template.txt` to define:
        *   The AI's persona/role.
        *   Its main objective for replies.
        *   Key information to include.
        *   Desired tone.
        *   Things the AI should avoid.
    *   This file has detailed inline instructions and examples.

6.  **Customize Email Filtering:**
    *   Edit `utils/filters.py`.
    *   Modify the `FILTER_PATTERNS` list. Each entry is a tuple: `(r'regex_pattern', 'reason_for_no_reply')`.
    *   Add, remove, or modify patterns to suit your needs. The file includes examples for common filters (out-of-office, automated) and placeholders for business-specific rules.

7.  **Review Agent Settings (Optional):**
    *   Open `agent.py`. You can adjust parameters like:
        *   `AI_MODEL_NAME` (if not set in `.env`)
        *   `MIN_REPLY_DELAY_HOURS`, `MAX_REPLY_DELAY_HOURS`
        *   `AGENT_START_HOUR_PST`, `AGENT_END_HOUR_PST`

## Running the Agent

Once configured, you can run the agent:

```bash
python agent.py
```

The agent will periodically check for new emails, filter them, generate replies for eligible emails, and send them.

## Development Notes

*   **`replies.json`**: Generated by `export_replies.py`, it contains a snapshot of emails. Useful for testing filters or AI prompts without hitting the API repeatedly.
*   **`email_reader.py`**: A simple script to pretty-print the contents of `replies.json`.
*   **Making it More Generic**: The current setup is a good starting point. To adapt it for completely different use cases, you'd primarily focus on heavily customizing `gpt/prompts/system_prompt_template.txt` and `utils/filters.py`.

## Contributing

If you'd like to contribute, please fork the repository and make a pull request.
(Further contribution guidelines can be added here if the project becomes public and open to contributions).

## License

MIT License
