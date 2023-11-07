import smtplib
from email.mime.text import MIMEText
from configs.email_conf import email_settings


def send_email(target_eamil, verify_code):
    msg = MIMEText(f"Verify code: {verify_code}", "html")
    msg["Subject"] = "no reply"
    msg["To"] = target_eamil
    msg["From"] = email_settings.ADDRESS
    # メール送信処理
    server = smtplib.SMTP(email_settings.HOST, email_settings.PORT)
    server.starttls()
    server.login(email_settings.ADDRESS, email_settings.PASSWORD)
    server.send_message(msg)
    server.quit()
