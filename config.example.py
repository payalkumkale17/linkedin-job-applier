# config.example.py — Copy this to config.py and fill in your values

# Apify — get token from: https://console.apify.com/account/integrations
APIFY_API_TOKEN = "your_apify_token_here"

# LinkedIn search keywords
SEARCH_KEYWORDS = ["Java Developer Contract"]

# Only consider posts from the last N hours
MAX_HOURS_OLD = 72

# Gmail OAuth2
GMAIL_CREDENTIALS_FILE = "credentials.json"
GMAIL_TOKEN_FILE = "token.json"

# Candidate details
SENDER_NAME      = "Your Full Name"
CANDIDATE_SKILLS = "Your skills here"

# Resume filename (must be in the same folder)
RESUME_PATH = "your_resume.pdf"
