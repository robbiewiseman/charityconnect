# VERSION 4 START

# Reference: Flask-Mail – sending emails and attachments (Pallets Projects, 2025)
# https://flask-mail.readthedocs.io/en/latest/

from flask import current_app
from flask_mail import Message

def send_receipt_email(mail, to_email: str, subject: str, body: str, pdf_bytes: bytes, filename: str):
    # Sends an email with a PDF receipt attached.

    # Create the email message
    msg = Message(
        subject=subject,
        recipients=[to_email],
        body=body,
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
    )

    # Attach the PDF receipt if it exists
    if pdf_bytes:
        msg.attach(
            filename=filename,
            content_type="application/pdf",
            data=pdf_bytes,
        )

    # Send the email using Flask-Mail
    mail.send(msg)
# VERSION 4 END