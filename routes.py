# VERSION 1

# Reference: routes.py was adapted from this ChatGPT template: https://chatgpt.com/share/690df926-fc70-8004-8452-e99ab50a799c

# This file defines all routes (URLs) and views for the CharityConnect application.
# It includes routes for public users, organisers, and admins.
# Each route connects frontend templates with backend database logic.

# VERSION 2 START
from flask import (Blueprint, render_template, redirect, url_for, request, flash, abort, session, Response, send_file, current_app)
import stripe, qrcode, io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from sqlalchemy import case
from sqlalchemy.exc import OperationalError
from extensions import csrf
from config import Config
from forms import PurchaseForm, ApplyVerificationForm, EventForm
# VERSION 2 END

from models import (db, User, Organiser, Charity, Event, EventBeneficiary, Order, Ticket, ROLE_USER, ROLE_ORG, ROLE_ADMIN)

# Reference: Flask Blueprints Documentation (Pallets Projects, 2024)
# https://flask.palletsprojects.com/en/stable/blueprints/
# Create a Flask Blueprint for routing
bp = Blueprint("main", __name__)

# REFERENCE: layout adapted from ChatGPT code: https://chatgpt.com/share/691d0c58-b260-8004-8756-d6215df38da4
# Reference: ReportLab Canvas API for building PDFs (ReportLab, 2025)
# https://docs.reportlab.com/reportlab/userguide/ch2_graphics/
# Reference: Python qrcode library – generating QR codes in memory (Lincoln Loop, 2025)
# https://pypi.org/project/qrcode/
# VERSION 2 START
def build_receipt_pdf(order):
    ev = order.event

    # Build verification URL for this order
    verify_url = url_for("main.order_verify", order_id=order.id, _external=True)

    # Create QR code image in memory
    qr_img = qrcode.make(verify_url)
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format="PNG")
    qr_buf.seek(0)
    qr_reader = ImageReader(qr_buf)  # ReportLab reads images in this format

    # Set up PDF buffer and canvas
    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf, pagesize=A4)
    width, height = A4

    # Basic text style for paragraphs
    body_style = ParagraphStyle(
        "body",
        alignment=TA_LEFT,
        fontSize=10,
        leading=14,
    )

    # Header bar
    header_height = 30 * mm
    c.setFillColor(colors.HexColor("#1E293B"))  # dark slate/navy
    c.rect(0, height - header_height, width, header_height, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, height - 18 * mm, "CharityConnect Receipt")

    # Order / event info
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    y = height - header_height - 15 * mm

    c.drawString(20 * mm, y, f"Order ID: {order.id}")
    y -= 5 * mm
    c.drawString(20 * mm, y, f"Event: {ev.title}")
    y -= 5 * mm
    if hasattr(ev, "starts_at") and ev.starts_at:
        c.drawString(20 * mm, y, f"Event date: {ev.starts_at.strftime('%Y-%m-%d %H:%M')}")
        y -= 5 * mm
    if hasattr(order, "created_at") and order.created_at:
        c.drawString(20 * mm, y, f"Order date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
        y -= 5 * mm
    if hasattr(order, "name"):
        c.drawString(20 * mm, y, f"Buyer: {getattr(order, 'name', '')}")
        y -= 5 * mm
    if hasattr(order, "email"):
        c.drawString(20 * mm, y, f"Email: {getattr(order, 'email', '')}")
        y -= 10 * mm

    # Line items (tickets / donations)
    line_y = y
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, line_y, "Description")
    c.drawRightString(width - 20 * mm, line_y, "Amount")
    line_y -= 6 * mm
    c.setFont("Helvetica", 10)

    total = 0
    # Expecting order.items or order.lines; adjust to your model
    items = getattr(order, "items", []) or getattr(order, "lines", [])
    for item in items:
        desc = getattr(item, "description", getattr(item, "label", "Item"))
        amount = getattr(item, "amount", 0)
        c.drawString(20 * mm, line_y, desc)
        c.drawRightString(width - 20 * mm, line_y, f"€{amount:0.2f}")
        total += amount
        line_y -= 5 * mm

    donation_eur = order.donation_cents / 100 if getattr(order, "donation_cents", None) is not None else 0
    total_eur = order.total_cents / 100 if getattr(order, "total_cents", None) is not None else 0

    donation_eur = (
        order.donation_cents / 100
        if getattr(order, "donation_cents", None) is not None
        else 0
    )

    total_eur = (
        order.total_cents / 100
        if getattr(order, "total_cents", None) is not None
        else total  # fallback to summed line items
    )

    # Totals
    line_y -= 4 * mm
    c.line(20 * mm, line_y, width - 20 * mm, line_y)
    line_y -= 6 * mm

    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, line_y, "Donation")
    c.drawRightString(width - 20 * mm, line_y, f"€{donation_eur:0.2f}")
    line_y -= 6 * mm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, line_y, "Total")
    c.drawRightString(width - 20 * mm, line_y, f"€{total_eur:0.2f}")
    y = line_y - 12 * mm

    # Beneficiary breakdown (if present)
    allocations = getattr(order, "allocations", None)
    if allocations:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20 * mm, y, "Beneficiary allocation")
        y -= 6 * mm
        c.setFont("Helvetica", 10)
        for alloc in allocations:
            charity_name = getattr(alloc, "charity_name", getattr(alloc, "charity", None))
            if hasattr(charity_name, "name"):
                charity_name = charity_name.name
            pct = getattr(alloc, "percentage", None)
            label_parts = []
            if charity_name:
                label_parts.append(str(charity_name))
            if pct is not None:
                label_parts.append(f"{pct}%")
            label = " ".join(label_parts) if label_parts else "Beneficiary"
            c.drawString(20 * mm, y, label)
            y -= 5 * mm
        y -= 8 * mm

    # QR code block
    qr_size = 35 * mm
    qr_x = width - 20 * mm - qr_size
    qr_y = 25 * mm
    c.drawImage(
        qr_reader,
        qr_x,
        qr_y,
        qr_size,
        qr_size,
        preserveAspectRatio=True,
        mask="auto",
    )

    # Text beside QR
    info_text = (
        "Scan this code or visit the link below to verify this receipt "
        "and view your order details:\n"
        f"{verify_url}"
    )
    p = Paragraph(info_text, body_style)
    text_width = qr_x - 25 * mm  # leave some padding before QR
    tw, th = p.wrap(text_width, 60 * mm)
    p.drawOn(c, 20 * mm, qr_y + (qr_size - th) / 2)

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(
        width / 2,
        10 * mm,
        "Thank you for supporting charity via CharityConnect.",
    )

    # Finalise PDF
    c.showPage()
    c.save()
    pdf_buf.seek(0)
    return pdf_buf.getvalue()

def finalise_order(order):
    # Saftey check
    if not order:
        return None
    # Marks order as paid if not already done
    if order.status != "PAID":
        order.status = "PAID"
    # Creates ticket records if they do not exist yet
    if not getattr(order, "tickets", None) or order.tickets.count() == 0:
        for i in range(order.qty):
            db.session.add(
                Ticket(order_id=order.id, code=f"T{order.id:06d}-{i+1:02d}")
            )
    # Generates and stores the receipt PDF if missing
    if hasattr(order, "receipt_pdf") and not order.receipt_pdf:
        try:
            pdf_bytes = build_receipt_pdf(order)
            order.receipt_pdf = pdf_bytes
        except Exception as e:
            current_app.logger.error(
                f"Receipt generation failed in finalise_order for order {order.id}: {e}"
            )
    # Saves everything to the database
    db.session.commit()
    return order
# VERSION 2 END

# Role System

# Simple session-based role control (user,organiser,admin)
def get_role():
    # Get the current user's role from the session (default: user)
    return session.get("role", ROLE_USER)

def set_role(role):
    # Set the user's role in the session, falling back to user if invalid
    if role not in (ROLE_USER, ROLE_ORG, ROLE_ADMIN):
        role = ROLE_USER
    session["role"] = role

# Restrict access to certain roles
def require_role(*roles):
    if get_role() not in roles:
        # Reference: Flask url_for redirect (Pallets Projects, 2024)
        # https://flask.palletsprojects.com/en/stable/quickstart/#url-building
        flash("Not authorised for this action.", "warning")
        return redirect(url_for("main.index"))
    return None

# VERSION 2 START
# Reference: Flask context processors – injecting variables into templates (Pallets Projects, 2025)
# https://flask.palletsprojects.com/en/stable/templating/#context-processors
# Template Processor
@bp.app_context_processor
def inject_current_role():
    return {"current_role": get_role(), "STRIPE_PUBLISHABLE_KEY": Config.STRIPE_PUBLISHABLE_KEY}
# VERSION 2 END

# Utility Function
def cents(eur_decimal):
    return int(round(float(eur_decimal or 0) * 100))

# Role switching
@bp.route("/role/<role>")
def switch_role(role):
    # Allows easy switching between roles for testing/admin purposes
    set_role(role)
    flash(f"Role switched to: {get_role()}", "info")
    return redirect(url_for("main.index"))

# VERSION 2 START
# Page where users can apply to become verified organisers
@bp.route("/apply", methods=["GET", "POST"])
def apply_verification():
    form = ApplyVerificationForm()
    # Reference: Flask-WTF form handling with validate_on_submit (Pallets Projects, 2025)
    # https://flask-wtf.readthedocs.io/en/1.2.x/quickstart/
    if form.validate_on_submit():
        org_type = form.org_type.data  # "organiser" or "charity"
        name = form.organisation_name.data.strip()
        charity_no = form.charity_number.data.strip() or None
        email = form.contact_email.data.lower()

        if org_type == "organiser":
            # Create an Organiser application
            obj = Organiser(
                organisation_name=name,
                charity_number=charity_no,
                contact_email=email,
                status="pending",
                verified=False,
            )
        else:
            # Create a Charity application
            obj = Charity(
                name=name,
                charity_number=charity_no,
                contact_email=email,
                status="pending",
                verified=False,
            )
        db.session.add(obj)
        db.session.commit()
        # Let the user know the application was received
        flash("Your application has been submitted for review.", "success")
        return redirect(url_for("main.index"))
    # Show the form if the user is just opening the page
    return render_template("apply_verification.html", form=form)
# VERSION 2 END

# Public Routes
@bp.route("/")
def index():
    # Display all published charity events on the homepage
    # Reference: SQLAlchemy Query Guide – filtering and ordering (SQLAlchemy, 2024)
    # https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html
    events = Event.query.filter_by(published=True).order_by(Event.starts_at.asc()).all()
    return render_template("index.html", events=events)

# VERSION 2 START
# Show a list of all published events
@bp.route("/events")
def events_list():
    # Get all events that are marked as published, sorted by start date
    events = Event.query.filter_by(published=True).order_by(Event.starts_at.asc()).all()
    # Display them on the events page
    return render_template("events.html", events=events)
# VERSION 2 END

@bp.route("/events/<int:event_id>")
def event_detail(event_id):
    # Show event details to users (only if event is published)
    ev = Event.query.get_or_404(event_id)
    if not ev.published and get_role() not in (ROLE_ORG, ROLE_ADMIN):
        abort(404)
    return render_template("event_detail.html", ev=ev)

@bp.route("/events/<int:event_id>/buy", methods=["GET","POST"])
def event_buy(event_id):
    # Handle the event ticket purchase and optional donation
    # Reference: Flask-WTF Quickstart – validate_on_submit (Pallets Projects, 2024)
    # https://flask-wtf.readthedocs.io/en/1.2.x/quickstart/
    ev = Event.query.get_or_404(event_id)
    if not ev.published and get_role() not in (ROLE_ORG, ROLE_ADMIN):
        abort(404)

    form = PurchaseForm()
    if form.validate_on_submit():
        # Calculate total cost (tickets + optional donation)
        qty = form.qty.data
        donation_c = cents(form.donation_eur.data)
        total_c = ev.ticket_price_cents * qty + donation_c

        # Create the order and related tickets
        order = Order(
            event_id=ev.id,
            # VERSION 2 START
            user_id=None,
            email=form.email.data.lower(),
            qty=qty,
            donation_cents=donation_c,
            total_cents=total_c,
            status="PENDING",
            # VERSION 2 END
        )
        db.session.add(order)
        db.session.flush()

        # VERSION 2 START
        # Build the Stripe items for checkout (ticket first)
        line_items = [
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": ev.title},
                    "unit_amount": ev.ticket_price_cents,
                },
                "quantity": qty,
            }
        ]

        # Add the donation as a separate item if there is one
        if donation_c > 0:
            line_items.append(
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {"name": "Donation"},
                        "unit_amount": donation_c, 
                    },
                    "quantity": 1,
                }
            )

        # Reference: https://docs.stripe.com/api/checkout/sessions/create
        # Built based on the Stripe Docs
        # Create the Stripe Checkout Session for payment
        session_obj = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=line_items,
            success_url=url_for(
                "main.order_detail", order_id=order.id, _external=True
            )
            + "?success=true&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for("main.event_detail", event_id=ev.id, _external=True),
            client_reference_id=str(order.id),
            metadata={
                "order_id": str(order.id),
                "event_id": str(ev.id),
                "donation_cents": str(donation_c),
            },
        )

        # Save the payment intent so the webhook can link the payment to the order
        order.stripe_payment_intent = session_obj.payment_intent
        db.session.commit()
        # Send the user to Stripe's checkout page
        return redirect(session_obj.url, code=303)
        # VERSION 2 END

    # Handle validation errors
    if request.method == "POST":
        for field, msgs in form.errors.items():
            for m in msgs:
                flash(f"{field}: {m}", "danger")
    return render_template("event_buy.html", ev=ev, form=form)

# VERSION 2 START
# Reference: Code adapted from Stripe Docs: https://docs.stripe.com/webhooks/quickstart?lang=python
# Set the secret key used by Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY
# Endpoint that Stripe calls to send payment events (webhook)
@bp.route("/stripe/webhook", methods=["POST"], endpoint="stripe_webhook")
@csrf.exempt
def stripe_webhook_handler():
    # Get the raw request body and Stripe signature header
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature", "")
    # Verify the event is really from Stripe
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return Response(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return Response(status=400)

    # Get the event type and main data object
    event_type = event.get("type", "")
    data = event["data"]["object"]

    order = None

    if event_type == "checkout.session.completed":
        # First try to find the order using the client_reference_id
        ref = data.get("client_reference_id")
        if ref:
            try:
                order = Order.query.get(int(ref))
            except Exception:
                order = None

        # If that fails, try matching by stored Stripe session/payment IDs
        if not order:
            sess_id = data.get("id")
            if sess_id:
                order = Order.query.filter_by(stripe_payment_intent=sess_id).first()

        if not order:
            pi_id = data.get("payment_intent")
            if pi_id:
                order = Order.query.filter_by(stripe_payment_intent=pi_id).first()

        # If we found an order, update it to store the PaymentIntent ID going forward
        if order and data.get("payment_intent"):
            order.stripe_payment_intent = data["payment_intent"]

        pass

    elif event_type == "payment_intent.succeeded":
        # For payment_intent events, look up the order by the payment intent ID
        pi_id = data.get("id")
        if pi_id:
            order = Order.query.filter_by(stripe_payment_intent=pi_id).first()

        pass

    # If we found an order from this event, mark it as paid and finish it
    if order:
        finalise_order(order)
    # Tell Stripe we handled the webhook

    return Response(status=200)

# Reference: SQLAlchemy engine dispose / reconnect pattern (SQLAlchemy, 2025)
# https://docs.sqlalchemy.org/en/20/core/connections.html#engine-disposal
def _safe_get_order_or_404(order_id):
    # Try to get an order, handling possible DB connection errors
    try:
        return Order.query.get_or_404(order_id)
    except OperationalError:
        # Reset the DB connection and try again
        db.engine.dispose()
        return Order.query.get_or_404(order_id)
# VERSION 2 END

@bp.route("/orders/<int:order_id>")
# Show order confirmation and details
def order_detail(order_id):
    # VERSION 2 START
    # Get the order or return 404 if it doesn't exist
    order = _safe_get_order_or_404(order_id)
    # Read query parameters from the URL
    success = request.args.get("success") == "true"
    session_id = request.args.get("session_id")
    paid = (order.status == "PAID")
    
    # Reference: Stripe Checkout Session retrieval in Python (Stripe, 2025)
    # https://docs.stripe.com/payments/checkout/fulfillment?lang=python
    # If we have just returned from Stripe checkout, check the session
    if success and session_id:
        try:
            # Ask Stripe for the latest info about this checkout session
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            # If Stripe says the session is paid, mark it as paid locally
            if checkout_session.payment_status == "paid":
                paid = True
                # Store the PaymentIntent ID on the order if missing
                if checkout_session.payment_intent and not order.stripe_payment_intent:
                    order.stripe_payment_intent = checkout_session.payment_intent
                db.session.commit()
            else:
                # Log if the session is not paid yet
                current_app.logger.warning(
                    f"Checkout session {session_id} not paid yet "
                    f"(status={checkout_session.payment_status})"
                )
        except Exception as e:
            # Log any error talking to Stripe
            current_app.logger.error(
                f"Error checking Stripe session {session_id} for order {order.id}: {e}"
            )

    # If we know the order is paid (from DB or Stripe), finalise it
    if paid or order.status == "PAID":
        finalise_order(order)              
    # VERSION 2 END
    return render_template("order_detail.html", order=order)

# VERSION 2 START
# Page to check if an order is valid and paid (used by the QR code)
@bp.route("/orders/<int:order_id>/verify")
def order_verify(order_id):
    # Get the order or return 404
    order = Order.query.get_or_404(order_id)
    # True if the order is paid
    ok = (order.status == "PAID")
    # Show the verification page
    return render_template("order_verify.html", order=order, ok=ok)

# Download the PDF receipt for an order
@bp.route("/orders/<int:order_id>/receipt")
def order_receipt(order_id):
    # Get the order safely, retrying if needed
    order = _safe_get_order_or_404(order_id)
    # If the order has no receipt stored, return 404
    if not order.receipt_pdf:
        abort(404)

    # Reference: Flask send_file helper for sending binary responses (Pallets Projects, 2025)
    # https://flask.palletsprojects.com/en/stable/api/#flask.send_file
    # Send the PDF file to the user
    return send_file(
        io.BytesIO(order.receipt_pdf),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"receipt_{order.id}.pdf",
    )
# VERSION 2 END

# Admin Routes
@bp.route("/admin/verify")
def admin_verify():
    guard = require_role(ROLE_ADMIN)
    if guard:
        return guard
    # VERSION 2 START
    # Reference: SQLAlchemy case expression for custom sort order (SQLAlchemy, 2025)
    # https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.case
    # Set a sort order based on organiser status (pending first, then verified, then rejected)
    status_order_org = case(
        (Organiser.status == "pending", 0),
        (Organiser.status == "verified", 1),
        (Organiser.status == "rejected", 2),
        else_=3
    )
    
    status_order_charity = case(
        (Charity.status == "pending", 0),
        (Charity.status == "verified", 1),
        (Charity.status == "rejected", 2),
        else_=3,
    )
    # Get all organisers, sorted by status and newest first
    orgs = Organiser.query.order_by(status_order_org, Organiser.id.desc()).all()
    charities = Charity.query.order_by(status_order_charity, Charity.id.desc()).all()
    return render_template("admin_verify.html", orgs=orgs, charities=charities)
    # VERSION 2 END

@bp.route("/admin/verify/<int:org_id>/toggle", methods=["POST"])
# Reference: CSRF API (disabled here for demo only) (Pallets Projects, 2024)
# https://flask-wtf.readthedocs.io/en/1.2.x/csrf/
@csrf.exempt  # CSRF disabled for simplicity in admin toggle (use with care)
# VERSION 2 START
def admin_verify_action(org_id):
    # Only admins can perform verification actions
    guard = require_role(ROLE_ADMIN)
    if guard:
        return guard

    # Get the organiser or return 404
    org = Organiser.query.get_or_404(org_id)
    # Read which action the admin submitted
    action = request.form.get("action", "").lower()

    # Update the organiser based on the chosen action
    if action == "verify":
        org.verified = True
        org.status = "verified"
        msg = "Organiser verified."
    elif action == "unverify":
        org.verified = False
        org.status = "pending"
        msg = "Organiser set to pending."
    elif action == "reject":
        org.verified = False
        org.status = "rejected"
        msg = "Organiser rejected."
    elif action == "restore":
        org.verified = False
        org.status = "pending"
        msg = "Organiser restored to pending."
    else:
        # If the action is unknown, show an error and return
        flash("Unknown action.", "danger")
        return redirect(url_for("main.admin_verify"))

    # Save the changes
    db.session.commit()
    # Show success message and return to the admin page
    flash(msg, "success")
    return redirect(url_for("main.admin_verify"))

@bp.route("/admin/verify/charity/<int:charity_id>", methods=["POST"])
def admin_verify_charity_action(charity_id):
    # Only admins can perform verification actions
    guard = require_role(ROLE_ADMIN)
    if guard:
        return guard
    # Fetch the charity record or return 404 if it doesn’t exist
    charity = Charity.query.get_or_404(charity_id)
    # Action comes from a hidden form field
    action = request.form.get("action", "").lower()
    # Update verification status based on the admin action
    if action == "verify":
        charity.verified = True
        charity.status = "verified"
        msg = "Charity verified."
    elif action == "unverify":
        charity.verified = False
        charity.status = "pending"
        msg = "Charity set to pending."
    elif action == "reject":
        charity.verified = False
        charity.status = "rejected"
        msg = "Charity rejected."
    elif action == "restore":
        charity.verified = False
        charity.status = "pending"
        msg = "Charity restored to pending."
    else:
        # Invalid or missing action
        flash("Unknown action.", "danger")
        return redirect(url_for("main.admin_verify"))
    # Save the update and notify the admin
    db.session.commit()
    flash(msg, "success")
    # Return to the verification dashboard
    return redirect(url_for("main.admin_verify"))
# VERSION 2 END

# Organiser Routes
@bp.route("/organiser/events/new", methods=["GET","POST"])
def event_new():
    guard = require_role(ROLE_ORG, ROLE_ADMIN)
    if guard:
        return guard
    # Allow organisers to create and publish charity events
    form = EventForm()

    # VERSION 2 START
    # Only verified charities appear as options
    verified_charities = (Charity.query.filter_by(verified=True).order_by(Charity.name.asc()).all())
    charity_choices = [(c.id, f"{c.name}") for c in verified_charities]
    if not charity_choices:
        flash("No verified charities are available yet. Ask an admin to verify at least one charity.", "info")

    # Apply choices to every beneficiary subform in the FieldList
    for b in form.beneficiaries:
        b.charity_id.choices = charity_choices

    # Add beneficiary (just add a row, no validation / 100% check)
    if request.method == "POST" and "add_beneficiary" in request.form:
        # add one more row
        form.beneficiaries.append_entry()
        # reapply choices for the new row as well
        for b in form.beneficiaries:
            b.charity_id.choices = charity_choices
        # just re-render the form, do NOT validate or save
        return render_template("event_new.html", form=form)

    # Save event (full validation and 100% rule)
    if form.validate_on_submit():
        total_alloc = sum(
            b.allocation_percent.data or 0
            for b in form.beneficiaries
        )
        if total_alloc != 100:
            flash("Allocation must total 100%.", "danger")
            return render_template("event_new.html", form=form)
    # VERSION 2 END

        # Fallback organiser (for if none exist)
        org = Organiser.query.first()
        if not org:
            org = Organiser(organisation_name="Fallback Organiser", charity_number="FBACK-000", verified=True)
            db.session.add(org)
            db.session.flush()

        # Create event record
        ev = Event(
            organiser_id=org.id,
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else "",
            venue=form.venue.data.strip() if form.venue.data else "",
            starts_at=form.starts_at.data,
            ticket_price_cents=cents(form.ticket_price_eur.data),
            published=bool(form.published.data),
        )
        db.session.add(ev)
        db.session.flush()

        # Add beneficiary allocations
        for b in form.beneficiaries:
            db.session.add(EventBeneficiary(
                event_id=ev.id,
                charity_id=b.form.charity_id.data,
                allocation_percent=b.form.allocation_percent.data
            )
        )
        
        # Reference: SQLAlchemy commit (SQLAlchemy, 2024)
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html
        db.session.commit()
        flash("Event saved.", "success")
        return redirect(url_for('main.event_detail', event_id=ev.id))

    # Handle form validation errors
    if request.method == "POST":
        for field, msgs in form.errors.items():
            for m in msgs:
                flash(f"{field}: {m}", "danger")

    return render_template("event_new.html", form=form)

# VERSION 1