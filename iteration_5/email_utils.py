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

# VERSION 5 START
def send_refund_decision_email(mail, to_email: str, event_title: str, approved: bool, organiser_note: str):
     # Send an email informing the user whether their refund request was approved or denied.

    # Determine decision wording for subject line
    status_word = "approved" if approved else "denied"
    # Email subject clearly states the decision and event
    subject = f"Your refund request has been {status_word.capitalize()} – {event_title}"

    # Build the main message depending on decision
    if approved:
        body = (
            f"Good news! Your refund request for '{event_title}' has been approved.\n\n"
            "The organiser will process your refund shortly.\n"
        )
    else:
        body = (
            f"Unfortunately, your refund request for '{event_title}' has been denied.\n\n"
        )

    # Include organiser message only if one exists
    if organiser_note:
        body += f"\nMessage from the organiser:\n{organiser_note}\n"

    # Standard closing message
    body += (
        "\nIf you have any questions, please contact the event organiser directly.\n\n"
        "CharityConnect"
    )

    # Create email message
    msg = Message(
        subject=subject,
        recipients=[to_email],
        body=body,
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
    )
    mail.send(msg)


def send_impact_summary_email(mail, to_email: str, event_title: str, event_date: str, user_contribution_eur: float, total_raised_eur: float, tickets_sold: int, allocations: list):
    # Send a post-event summary showing how the user's contribution was distributed.

    # Subject highlights the purpose of the email
    subject = f"Your Impact: {event_title}"

    # Start building the email body with event overview
    body = (
        f"Thank you for supporting {event_title}.\n\n"
        f"The event took place on {event_date} and was a success. "
        "Here’s the impact your contribution made:\n\n"
        # Personal contribution section
        "Your contribution\n"
        "-----------------\n"
        f"€{user_contribution_eur:.2f}\n\n"
        # Overall event totals
        "Event totals\n"
        "------------\n"
        f"Total raised: €{total_raised_eur:.2f}\n"
        f"Tickets sold: {tickets_sold}\n\n"
        # Allocation breakdown header
        "How your contribution was allocated\n"
        "-----------------------------------\n"
    )

    # List how the contribution was split across charities
    for alloc in allocations:
        body += f"{alloc['charity_name']}: {alloc['percent']}% = €{alloc['amount_eur']:.2f}\n"

    # Closing message
    body += (
        "\nThank you for making a difference through CharityConnect. "
        "Your support helps these charities continue their important work.\n\n"
        "If you have any questions, please contact the event organiser.\n\n"
        "CharityConnect Team"
    )

    # Create email message
    msg = Message(
        subject=subject,
        recipients=[to_email],
        body=body,
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
    )
    mail.send(msg)
# VERSION 5 END
# VERSION 4 END