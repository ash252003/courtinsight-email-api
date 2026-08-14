import logging
import os

import httpx
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, EmailStr, field_validator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mailer")

app = FastAPI()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")  # e.g. "Your App <onboarding@resend.dev>"
API_KEY = os.getenv("MAILER_API_KEY")  # shared secret for callers of this API

if not RESEND_API_KEY:
    raise RuntimeError("RESEND_API_KEY env var must be set")
if not FROM_EMAIL:
    raise RuntimeError("FROM_EMAIL env var must be set")
if not API_KEY:
    raise RuntimeError("MAILER_API_KEY env var must be set")

RESEND_URL = "https://api.resend.com/emails"


class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    message: str

    @field_validator("subject")
    @classmethod
    def no_header_injection(cls, v: str) -> str:
        if "\n" in v or "\r" in v:
            raise ValueError("Subject cannot contain newlines")
        if len(v) > 200:
            raise ValueError("Subject too long")
        return v

    @field_validator("message")
    @classmethod
    def message_length(cls, v: str) -> str:
        if len(v) > 20000:
            raise ValueError("Message too long")
        return v


@app.post("/send-email")
def send_email(req: EmailRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    payload = {
        "from": FROM_EMAIL,
        "to": [req.to],
        "subject": req.subject,
        "text": req.message,
    }
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = httpx.post(RESEND_URL, json=payload, headers=headers, timeout=10)
    except httpx.RequestError:
        logger.exception("Network error calling Resend")
        raise HTTPException(status_code=502, detail="Failed to reach email provider")

    if response.status_code >= 400:
        logger.error("Resend API error: %s %s", response.status_code, response.text)
        raise HTTPException(status_code=502, detail="Failed to send email")

    data = response.json()
    return {"status": "sent", "id": data.get("id")}
