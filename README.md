# 🤖 LinkedIn to Gmail Job Auto-Applier

An automation tool that scrapes recent LinkedIn job posts, extracts recruiter email addresses, and sends personalized application emails with a resume attachment — all automatically.

Built by **Payal Kumkale** as part of a job application automation project.

---

✨ What It Does

1. **Scrapes LinkedIn posts** — searches for keywords like `"Java Developer Contract"` posted in the last 24 hours
2. **Extracts recruiter emails** — finds email addresses directly from post text using regex
3. **Sends application emails** — logs into Gmail via OAuth2 and sends a formal email with resume attached to each recruiter

---

📊 Results

- ✅ 50 LinkedIn posts scraped per run
- ✅ ~24 recruiter emails extracted per run
- ✅ ~18 unique emails sent per run (duplicates skipped)
- ✅ Runs in under 2 minutes

---

 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.x | Core language |
| Apify | LinkedIn post scraping (no cookies needed) |
| Gmail API | Sending emails via OAuth2 |
| google-auth-oauthlib | Gmail authentication |
| regex | Email extraction from post text |

---

📁 Project Structure

```
linkedin-job-applier/
├── main.py              # Main automation script
├── config.py            # Your settings (not in repo — see config.example.py)
├── config.example.py    # Template for config.py
├── requirements.txt     # Python dependencies
├── SETUP_GUIDE.md       # Detailed step-by-step setup instructions
├── .gitignore           # Protects secrets from being pushed
└── README.md            # This file
```

---

⚡ Quick Start

1. Clone the repo
```bash
git clone https://github.com/payalkumkale17/linkedin-job-applier.git
cd linkedin-job-applier
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up config
```bash
cp config.example.py config.py
```
Open `config.py` and fill in:
- Your Apify API token
- Your name and skills
- Your resume filename

4. Set up Gmail API
Follow the detailed instructions in **SETUP_GUIDE.md** to:
- Create a Google Cloud project
- Enable Gmail API
- Download `credentials.json`

### 5. Run
```bash
python main.py
```
A browser window opens once for Gmail login. After that it runs fully automatically.

---

⚙️ Configuration

| Setting | Description |
|---|---|
| `APIFY_API_TOKEN` | From https://console.apify.com/account/integrations |
| `SEARCH_KEYWORDS` | e.g. `["Java Developer Contract"]` |
| `MAX_HOURS_OLD` | Only scrape posts from last N hours (default: 24) |
| `SENDER_NAME` | Your full name |
| `CANDIDATE_SKILLS` | Your top skills for the email body |
| `RESUME_PATH` | Filename of your resume PDF |

---

🔒 Security

The following files are **never committed** to this repo (protected by `.gitignore`):
- `config.py` — contains your Apify token
- `credentials.json` — Google OAuth client secret
- `token.json` — Gmail access token
- `cookies.json` — LinkedIn session cookies

---

📬 Sample Email Sent

> **Subject:** Application for Java Developer (Contract) Position
>
> Dear Hiring Manager / Recruiter,
>
> I came across your recent LinkedIn post regarding a Java Developer (Contract) opportunity and I would like to express my interest...
>
> [Resume attached as PDF]

---

🚀 Run Daily for Best Results

```bash
cd linkedin-job-applier
python main.py
```

Fresh recruiter posts appear every day — running every morning maximizes response rate.

---

📄 License

MIT License — free to use and modify.

---

👩‍💻 Author

**Payal Kumkale**
- 📧 payalkumkale17@gmail.com
- 🔗 [LinkedIn](https://linkedin.com/in/payalkumkale17)
- 🐙 [GitHub](https://github.com/payalkumkale17)
