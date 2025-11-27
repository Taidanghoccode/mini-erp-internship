import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SMTP_USER = "tainhce181569@fpt.edu.vn"
SMTP_PASS = "ynjr tdqx gieo nizl"


class MailService:
    def send_mail(self, to_email, subject, text_body):
        try:
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = SMTP_USER
            msg["To"] = to_email

            msg.attach(MIMEText(text_body, "plain"))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, to_email, msg.as_string())

            print("Email sent successfully!")
            return True

        except Exception as e:
            print("MAIL ERROR:", e)
            return False
