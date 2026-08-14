@app.post("/send-email")
def send_email(req: EmailRequest):
    print("===== REQUEST RECEIVED =====")
    print(req)

    msg = MIMEText(req.message)
    msg["Subject"] = req.subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = req.to

    print("Connecting to Gmail...")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
        print("Connected")

        print("Logging in...")
        server.login(SMTP_EMAIL, SMTP_PASSWORD)

        print("Logged in")

        print("Sending...")
        server.send_message(msg)

        print("Sent")

    return {"status": "Email sent"}
