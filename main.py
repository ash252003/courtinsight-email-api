from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, EmailStr, field_validator
import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.utils import formataddr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mailer")

app = FastAPI()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
API_KEY = os.getenv("MAILER_API_KEY")  # simple shared-secret auth

if not SMTP_EMAIL or not SMTP_PASSWORD:
    raise RuntimeError("SMTP_EMAIL and SMTP_PASSWORD env vars must be set")
if not API_KEY:
    raise RuntimeError("MAILER_API_KEY env var must be set")


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

    msg = MIMEText(req.message)
    msg["Subject"] = req.subject
    msg["From"] = formataddr(("Your App", SMTP_EMAIL))
    msg["To"] = req.to

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
    except smtplib.SMTPException:
        logger.exception("SMTP send failed")
        raise HTTPException(status_code=502, detail="Failed to send email")
    except Exception:
        logger.exception("Unexpected error sending email")
        raise HTTPException(status_code=500, detail="Internal server error")

    return {"status": "sent"}
