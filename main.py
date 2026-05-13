"""
LinkedIn Job Auto-Applier
=========================
Flow:
  1. Scrape LinkedIn posts via Apify for keywords + last 24h
  2. Extract recruiter email from post text
  3. Send application email via Gmail API (OAuth2) with resume attached

Run:
  python main.py
"""

import re
import sys
import time
import base64
import logging
import datetime
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from apify_client import ApifyClient
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from config import (
    APIFY_API_TOKEN,
    GMAIL_CREDENTIALS_FILE,
    GMAIL_TOKEN_FILE,
    RESUME_PATH,
    SENDER_NAME,
    CANDIDATE_SKILLS,
    SEARCH_KEYWORDS,
    MAX_HOURS_OLD,
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# STEP 1 + 2 : Scrape LinkedIn posts via Apify

def scrape_linkedin_posts():
    log.info("Starting Apify LinkedIn scrape ...")
    client = ApifyClient(APIFY_API_TOKEN)

    run_input = {
        "keyword": SEARCH_KEYWORDS[0],
        "totalPostsToScrape": 50,
        "sortBy": "date_posted",
        
    }

    log.info("   Running actor: apimaestro/linkedin-posts-search-scraper-no-cookies")
    run = client.actor("apimaestro/linkedin-posts-search-scraper-no-cookies").call(run_input=run_input)
    dataset_id = run["defaultDatasetId"]

    items = list(client.dataset(dataset_id).iterate_items())
    log.info(f"   Apify returned {len(items)} raw posts")

    # Debug: show date-related fields from first post
    if items:
        log.info(f"   Post fields: {list(items[0].keys())}")
        for k, v in items[0].items():
            if any(x in k.lower() for x in ["date","time","post","ago","when","publish"]):
                log.info(f"   Date field -> {k}: {v}")

    cutoff = time.time() - (MAX_HOURS_OLD * 3600)
    recent = []
    for item in items:
        # posted_at is a dict: {display_text, date, timestamp}
        posted_at_field = item.get("posted_at") or {}
        if isinstance(posted_at_field, dict):
            posted_raw = posted_at_field.get("timestamp") or posted_at_field.get("date") or 0
        else:
            posted_raw = posted_at_field or 0
        now = time.time()
        if isinstance(posted_raw, str):
            s = posted_raw.lower().strip()
            try:
                if "hour" in s:
                    posted = now - int(re.search(r"\d+", s).group()) * 3600
                elif "minute" in s or "min" in s:
                    posted = now - int(re.search(r"\d+", s).group()) * 60
                elif "day" in s:
                    posted = now - int(re.search(r"\d+", s).group()) * 86400
                elif "week" in s:
                    posted = now - int(re.search(r"\d+", s).group()) * 604800
                elif "just now" in s or "second" in s:
                    posted = now
                else:
                    posted = datetime.datetime.fromisoformat(
                        posted_raw.replace("Z", "+00:00")).timestamp()
            except Exception:
                posted = 0
        else:
            posted = float(posted_raw) if posted_raw else 0
            # Convert milliseconds to seconds if needed
            if posted > 9999999999:
                posted = posted / 1000
        if posted >= cutoff:
            recent.append(item)

    if not recent and items:
        log.warning(f"   Date filter removed all posts — using all {len(items)} posts")
        return items

    log.info(f"   {len(recent)} posts within last {MAX_HOURS_OLD}h")
    return recent


# STEP 3 : Extract recruiter email from post text

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

def extract_email(post):
    text = post.get("text") or post.get("content") or post.get("description") or ""
    matches = EMAIL_REGEX.findall(text)
    filtered = [m for m in matches if not m.lower().endswith((".png", ".jpg", ".gif"))]
    return filtered[0] if filtered else None


def enrich_posts(posts):
    enriched = []
    for post in posts:
        email = extract_email(post)
        if email:
            post["recruiter_email"] = email
            enriched.append(post)
            log.info(f"   Found email: {email}  |  {str(post.get('url',''))[:60]}")
    log.info(f"   {len(enriched)} / {len(posts)} posts had a recruiter email")
    return enriched


# STEP 4 : Gmail API

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_gmail_service():
    creds = None
    token_path = Path(GMAIL_TOKEN_FILE)

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), GMAIL_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            log.info("   Refreshing Gmail token ...")
            creds.refresh(Request())
        else:
            log.info("   Opening browser for Gmail OAuth2 consent ...")
            flow = InstalledAppFlow.from_client_secrets_file(
                GMAIL_CREDENTIALS_FILE, GMAIL_SCOPES
            )
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
        log.info(f"   Token saved to {GMAIL_TOKEN_FILE}")

    return build("gmail", "v1", credentials=creds)


def build_email(to_email, post):
    msg = MIMEMultipart()
    msg["To"] = to_email
    msg["From"] = SENDER_NAME
    msg["Subject"] = "Application for Java Developer (Contract) Position"

    body = f"""Dear Hiring Manager / Recruiter,

I came across your recent LinkedIn post regarding a Java Developer (Contract) opportunity and I would like to express my interest in this position.

I am Payal Kumkale, a B.Tech CSE student at MIT ADT University, Pune (CGPA: 8.38), with hands-on experience in {CANDIDATE_SKILLS}. I hold a certification in Object Oriented Programming in Java from Coursera and have applied my technical skills across multiple AI-driven projects, including a published peer-reviewed research paper in IJSREM (Impact Factor: 8.659).

I am available for contract engagements and am eager to contribute meaningfully to your team. Please find my resume attached for your review.

I would welcome the opportunity to discuss how my background aligns with your requirements.

Thank you for your time and consideration. I look forward to hearing from you.

Best regards,
{SENDER_NAME}
payalkumkale17@gmail.com | +91 93596 98449
"""

    msg.attach(MIMEText(body, "plain"))

    resume_path = Path(RESUME_PATH)
    if not resume_path.exists():
        log.warning(f"   Resume not found at {RESUME_PATH} — sending without attachment")
    else:
        with open(resume_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{resume_path.name}"')
        msg.attach(part)
        log.info(f"   Attached resume: {resume_path.name}")

    return msg


def send_email(service, msg):
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    try:
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return True
    except Exception as e:
        log.error(f"   Gmail send failed: {e}")
        return False


# Main

def main():
    log.info("=" * 55)
    log.info("  LinkedIn to Gmail Auto-Applier")
    log.info("=" * 55)

    posts = scrape_linkedin_posts()
    if not posts:
        log.warning("No recent posts found. Check your keywords or Apify token.")
        sys.exit(0)

    posts_with_email = enrich_posts(posts)
    if not posts_with_email:
        log.warning("Found posts but none contained a recruiter email address.")
        sys.exit(0)

    log.info("Authenticating Gmail ...")
    gmail = get_gmail_service()
    log.info("   Gmail ready")

    seen_emails = set()
    sent = 0
    skipped = 0

    for post in posts_with_email:
        recruiter_email = post["recruiter_email"]

        if recruiter_email in seen_emails:
            skipped += 1
            continue

        seen_emails.add(recruiter_email)
        log.info(f"Sending to {recruiter_email} ...")
        msg = build_email(recruiter_email, post)

        if send_email(gmail, msg):
            sent += 1
            log.info(f"   Sent to {recruiter_email}")
        else:
            log.error(f"   Failed: {recruiter_email}")

        time.sleep(2)

    log.info("=" * 55)
    log.info(f"  Done. Sent: {sent}  |  Skipped duplicates: {skipped}")
    log.info("=" * 55)


if __name__ == "__main__":
    main()
