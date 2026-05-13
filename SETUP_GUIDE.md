# Setup Guide — LinkedIn Job Auto-Applier

Follow these steps in order. Takes about 15–20 minutes total.

---

## Step 1 — Install Python dependencies

Open a terminal in the project folder and run:

```bash
pip install -r requirements.txt
```

---

## Step 2 — Get your Apify API token

1. Go to https://apify.com and create a free account
2. After signing in, go to: https://console.apify.com/account/integrations
3. Copy your **Personal API token**
4. Open `config.py` and paste it as the value of `APIFY_API_TOKEN`

> **Free plan includes $5 of compute credits** — enough for hundreds of runs.

---

## Step 3 — Set up Google Cloud (Gmail API)

### 3a. Create a project

1. Go to https://console.cloud.google.com
2. Click the project dropdown (top left) → **New Project**
3. Name it anything, e.g. `job-applier` → click **Create**

### 3b. Enable Gmail API

1. In the left menu go to **APIs & Services → Library**
2. Search for **Gmail API** → click it → click **Enable**

### 3c. Create OAuth2 credentials

1. Go to **APIs & Services → Credentials**
2. Click **+ Create Credentials → OAuth client ID**
3. If prompted, configure the consent screen first:
   - User type: **External** → Create
   - App name: anything (e.g. `Job Applier`)
   - Support email: your Gmail address
   - Scroll down → Save and Continue (skip optional fields)
   - On **Scopes** page → Save and Continue
   - On **Test users** page → click **+ Add users** → add your own Gmail address → Save
4. Back at **Create OAuth client ID**:
   - Application type: **Desktop app**
   - Name: anything → click **Create**
5. Click **Download JSON** on the popup
6. Rename the downloaded file to `credentials.json`
7. Place `credentials.json` in the same folder as `main.py`

---

## Step 4 — Add your resume

1. Copy your resume PDF into the project folder
2. Open `config.py` and set `RESUME_PATH` to the filename, e.g.:
   ```python
   RESUME_PATH = "John_Doe_Resume.pdf"
   ```

---

## Step 5 — Update your details in config.py

Open `config.py` and fill in:

| Setting | What to put |
|---|---|
| `APIFY_API_TOKEN` | From Step 2 |
| `SENDER_NAME` | Your full name |
| `CANDIDATE_SKILLS` | Your top Java skills (comma-separated) |
| `SEARCH_KEYWORDS` | Keep as `["Java Developer Contract"]` or customize |
| `RESUME_PATH` | Your resume filename |

---

## Step 6 — Run it

```bash
python main.py
```

**First run only:** A browser window will open asking you to sign in to Google and grant permission to send emails. Click **Allow**. This only happens once — the token is saved to `token.json`.

---

## Project folder should look like this before running

```
linkedin_job_apply/
├── main.py
├── config.py
├── requirements.txt
├── credentials.json      ← downloaded from Google Cloud
├── resume.pdf            ← your resume
└── token.json            ← auto-created on first run
```

---

## Troubleshooting

| Error | Fix |
|---|---|
| `apify_client not found` | Run `pip install -r requirements.txt` |
| `credentials.json not found` | Re-read Step 3c — make sure file is in same folder |
| `No recent posts found` | Try broader keywords or increase `MAX_HOURS_OLD` to 48 |
| `Gmail send failed: 403` | Make sure your Gmail is added as a Test User (Step 3c) |
| `Token expired` | Delete `token.json` and re-run — it will re-authenticate |

---

## Costs

| Service | Cost |
|---|---|
| Apify | Free tier: $5 credits/month. One LinkedIn scrape ≈ $0.05–0.20 |
| Gmail API | Completely free |
| Google Cloud | Free (OAuth2 for desktop apps has no billing) |
