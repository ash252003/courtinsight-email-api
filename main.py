from fastapi import FastAPI
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
import os

app = FastAPI()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

class EmailRequest(BaseModel):
    to: str
    subject: str
    message: str

@app.post("/send-email")
def send_email(req: EmailRequest):

    msg = MIMEText(req.message)
    msg["Subject"] = req.subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = req.to

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)

    return {"status": "Email sent"}
