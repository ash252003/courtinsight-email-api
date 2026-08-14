from fastapi import HTTPException
import traceback

@app.post("/send-email")
def send_email(req: EmailRequest):
    try:
        print("Request received:", req)

        msg = MIMEText(req.message)
        msg["Subject"] = req.subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = req.to

        print("Connecting to SMTP...")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            print("Connected")

            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            print("Logged in")

            server.send_message(msg)
            print("Email sent")

        return {"status": "Email sent"}

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
