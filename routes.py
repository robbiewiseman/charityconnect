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
from sqlalchemy.exc import OperationalError
from extensions import csrf
from config import Config
# VERSION 3 START
from sqlalchemy import case, func
from forms import PurchaseForm, ApplyVerificationForm, EventForm, RegisterForm, LoginForm, AccountForm
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from openrouter_client import chat, OpenRouterError
# VERSION 3 END
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
    if current_user.is_authenticated:
        return current_user.role
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

# VERSION 3 START

# Reference: Flask-Login user session management (Flask-Login, 2026)
# https://flask-login.readthedocs.io/en/latest/
# Used here for: login_user(), logout_user(), @login_required, and loading the logged-in user from a stored ID.

def get_current_user():
    # Get the logged-in user ID from the session
    uid = session.get("user_id")
    # If no user is logged in, return None
    if not uid:
        return None
    return User.query.get(uid)

@bp.route("/register", methods=["GET", "POST"])
def register():
    # Create the registration form
    form = RegisterForm()
    # Handle form submission
    if form.validate_on_submit():
        # Normalise email input
        email = form.email.data.lower().strip()

        # Prevent duplicate registrations
        if User.query.filter_by(email=email).first():
            flash("That email is already registered. Please log in.", "warning")
            return redirect(url_for("main.login"))

        # Decide role based on organiser checkbox
        role = ROLE_ORG if form.as_organiser.data else ROLE_USER

        # Create the user record
        user = User(email=email, name=form.name.data.strip(), role=role)

        user.set_password(form.password.data)
        # Record consent timestamp at registration
        user.consent_registered_at = datetime.utcnow()
        db.session.add(user)
        db.session.flush()

        # If registering as organiser, create organiser profile
        if form.as_organiser.data:
            org = Organiser(
                user_id=user.id,
                organisation_name=(form.org_name.data or "").strip(),
                charity_number=(form.charity_number.data or "").strip() or None,
                org_type="organiser",
                status="pending",
                verified=False,
                contact_name=user.name,
                contact_email=user.email,
            )
            db.session.add(org)

        # Save everything to the database
        db.session.commit()

        # Reference: Flask-Login logging a user in (Flask-Login, 2026)
        # https://flask-login.readthedocs.io/en/latest/#login-example
        # Log the user in immediately
        login_user(user)
        flash("Account created. You are now logged in.", "success")
        return redirect(url_for("main.index"))
    # Show registration page
    return render_template("register.html", form=form)

@bp.route("/login", methods=["GET", "POST"])
def login():
    # Create the login form
    form = LoginForm()
    # Handle form submission
    if form.validate_on_submit():
        # Normalise email input
        email = form.email.data.lower().strip()
        # Look up the user
        user = User.query.filter_by(email=email).first()

        # Reject invalid credentials
        if not user or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
            return render_template("login.html", form=form)

        # Log the user in
        login_user(user)
        flash("Logged in successfully.", "success")
        # Redirect to original page if present
        next_url = request.args.get("next")
        return redirect(next_url or url_for("main.index"))
    # Show login page
    return render_template("login.html", form=form)

@bp.route("/logout")
# Reference: Flask-Login protecting routes (Flask-Login, 2026) 
# https://flask-login.readthedocs.io/en/latest/
@login_required
def logout():
    # Reference: Flask-Login logging a user out (Flask-Login, 2026)
    # https://flask-login.readthedocs.io/en/latest/#login-example
    # End the user session
    logout_user()
    # Inform the user
    flash("You have been logged out.", "info")
    # Redirect to homepage
    return redirect(url_for("main.index"))
# VERSION 3 END

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
    # VERSION 3 START
    if not current_app.debug:
        abort(404)
    # VERSION 3 END
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
        # VERSION 3 START
        # Record when consent was captured at checkout
        order.consent_checkout_at = datetime.utcnow()
        # Store the IP address for audit (uses X-Forwarded-For if behind a proxy)
        order.consent_checkout_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        # Store the browser/device user-agent (trimmed to fit DB column length)
        order.consent_checkout_ua = request.headers.get("User-Agent", "")[:255]
        # VERSION 3 END

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

# VERSION 3 START
@bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    # Initialise the account update form
    form = AccountForm()

    if request.method == "GET":
        # Pre-fill the form with the current user's details
        form.name.data = current_user.name or ""
        form.email.data = current_user.email or ""
        # Convert stored value to reminder boolean for the checkbox
        form.marketing_consent.data = bool(getattr(current_user, "marketing_consent", False))

    if form.validate_on_submit():
        # Normalise the new email address
        new_email = form.email.data.strip().lower()
        # Check the email is not already used by another account
        existing = User.query.filter(User.email == new_email, User.id != current_user.id).first()
        if existing:
            flash("That email is already in use.", "danger")
            return render_template("account.html", form=form)

        # Update basic account details
        current_user.name = form.name.data.strip()
        current_user.email = new_email

        # Handle marketing consent changes with audit trail
        previous = bool(getattr(current_user, "marketing_consent", False))
        new_value = bool(form.marketing_consent.data)

        if new_value != previous:
            current_user.marketing_consent = new_value
            if new_value:
                # Record when consent was given
                current_user.marketing_consent_at = datetime.utcnow()
            else:
                # Record when consent was withdrawn
                current_user.marketing_consent_withdrawn_at = datetime.utcnow()

        # Save changes to the database
        db.session.commit()
        flash("Account updated.", "success")
        return redirect(url_for("main.account"))

    if request.method == "POST":
        # Surface any form validation errors to the user
        for field, msgs in form.errors.items():
            for m in msgs:
                flash(f"{field}: {m}", "danger")
    # Render the account page
    return render_template("account.html", form=form)
# VERSION 3 END

# Admin Routes
@bp.route("/admin/verify")
# VERSION 3 START
@login_required
# VERSION 3 END
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
# VERSION 3 START
@login_required
# VERSION 3 END
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
# VERSION 3 START
@login_required
# VERSION 3 END
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

# VERSION 3 START

# Helper to ensure only organisers or admins can access AI features
def _ai_guard():
    # Check if current user has organiser or admin role
    guard = require_role(ROLE_ORG, ROLE_ADMIN)
    if guard:
        return guard
    return None

# AI route to suggest an event description
@bp.route("/ai/event-description", methods=["POST"])
@login_required
@csrf.exempt
def ai_event_description():
    # Block access if user is not organiser/admin
    g = _ai_guard()
    if g:
        return g

    # Reference: Flask Request.get_json() for parsing JSON request bodies (Pallets Projects, 2024)
    # https://flask.palletsprojects.com/en/stable/api/#flask.Request.get_json
    data = request.get_json(silent=True) or {}
    # Extract event details
    title = (data.get("title") or "").strip()
    venue = (data.get("venue") or "").strip()
    starts_at = (data.get("starts_at") or "").strip()
    ticket_price = (data.get("ticket_price") or "").strip()
    beneficiaries = data.get("beneficiaries") or []

    # Title is mandatory for generating a description
    if not title:
        return {"ok": False, "error": "Title is required."}, 400

    # Build beneficiary summary line for the AI prompt
    ben_line = ""
    parts = []
    for b in beneficiaries[:5]:
        name = (b.get("name") or "").strip()
        pct = b.get("pct")
        if name:
            parts.append(f"{name} ({pct}%)" if pct is not None else name)
    if parts:
        ben_line = "Beneficiaries: " + ", ".join(parts)

    # Prompt structure (system + user) to control tone and prevent fabricated claims
    # Reference: Prompt engineering guidance (OpenAI, 2024)
    # https://platform.openai.com/docs/guides/prompt-engineering
    # Messages sent to OpenRouter model
    messages = [
        {
            "role": "system",
            "content": (
                "Write a clear, trustworthy charity event description for a ticketing website. "
                "No made-up facts or stats. Use Irish/UK English. Return only the description text."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Write 90–140 words for this event:\n"
                f"Title: {title}\n"
                f"Venue: {venue or 'TBC'}\n"
                f"Start: {starts_at or 'TBC'}\n"
                f"Ticket price: {ticket_price or 'TBC'}\n"
                f"{ben_line}\n\n"
                "Include what attendees can expect, who it supports, and a call to action."
            ),
        },
    ]

    # Call OpenRouter and return generated description
    try:
        # Send chat-completions style request via OpenRouter using an OpenAI-compatible client
        # Reference: OpenRouter API documentation – OpenAI-compatible chat completions (OpenRouter, 2024)
        # https://openrouter.ai/docs
        text = chat(messages, temperature=0.7, max_tokens=220)
        return {"ok": True, "text": text.strip()}
    except OpenRouterError as e:
        return {"ok": False, "error": str(e)}, 502

# AI route to generate advertising suggestions for a specific event
@bp.route("/ai/ad-suggestions/<int:event_id>", methods=["POST"])
@login_required
@csrf.exempt
def ai_ad_suggestions_for_event(event_id):
    # Ensure user is organiser or admin
    guard = require_role(ROLE_ORG, ROLE_ADMIN)
    if guard:
        return guard

    # Load event and enforce ownership
    ev, org = _get_event_for_current_organiser_or_404(event_id)

    # Collect beneficiary data for the prompt
    beneficiaries = []
    for b in ev.beneficiaries:
        beneficiaries.append({"name": b.charity.name, "pct": b.allocation_percent})

    # Build beneficiary summary
    ben_names = [b["name"] for b in beneficiaries]
    ben_line = ", ".join(ben_names[:5]) if ben_names else "selected charities"

    # Messages sent to OpenRouter model
    messages = [
        {
            "role": "system",
            "content": (
                "You are a practical marketing assistant for a local Irish charity event. "
                "No fake partnerships, no inflated claims. Return structured bullet points."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Create an advertising plan for:\n"
                f"Title: {ev.title}\n"
                f"Venue: {ev.venue or 'TBC'}\n"
                f"Start: {ev.starts_at.strftime('%Y-%m-%d %H:%M') if ev.starts_at else 'TBC'}\n"
                f"Ticket price: €{ev.ticket_price_cents/100:.2f}\n"
                f"Beneficiaries: {ben_line}\n\n"
                "Return:\n"
                "1) 3 audience segments (who, why they care)\n"
                "2) 5 best channels for Cork/Ireland with a tactic each\n"
                "3) 2 Instagram captions, 2 Facebook posts, 1 email subject + short body\n"
                "4) 10 hashtag ideas"
            ),
        },
    ]

    # Call OpenRouter and return advertising suggestions
    try:
        text = chat(messages, temperature=0.6, max_tokens=650)
        return {"ok": True, "text": text.strip()}
    except OpenRouterError as e:
        return {"ok": False, "error": str(e)}, 502

# Fetch organiser profile for the logged-in user
def _get_current_organiser_or_redirect():
    org = Organiser.query.filter_by(user_id=current_user.id).first()
    if not org:
        flash("Your organiser account is not linked to an organiser profile.", "danger")
        return None
    return org

# Fetch an event and ensure it belongs to the logged-in organiser
def _get_event_for_current_organiser_or_404(event_id):
    org = Organiser.query.filter_by(user_id=current_user.id).first()
    if not org:
        abort(403)
    ev = Event.query.get_or_404(event_id)
    # Prevent access to events owned by other organisers
    if ev.organiser_id != org.id:
        abort(403)
    return ev, org

# VERSION 3 END

@bp.route("/organiser/events/new", methods=["GET","POST"])
# VERSION 3 START
@login_required
# VERSION 3 END
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
        total_alloc = sum(b.allocation_percent.data or 0 for b in form.beneficiaries)
        if total_alloc != 100:
            flash("Allocation must total 100%.", "danger")
            return render_template("event_new.html", form=form)
    # VERSION 2 END

        # Fallback organiser (for if none exist)
        # VERSION 3 START
        org = Organiser.query.filter_by(user_id=current_user.id).first()
        if not org:
            flash("Your organiser account is not linked to an organiser profile.", "danger")
            return redirect(url_for("main.index"))

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
        return redirect(url_for("main.organiser_events"))
        # VERSION 3 END

    # Handle form validation errors
    if request.method == "POST":
        for field, msgs in form.errors.items():
            for m in msgs:
                flash(f"{field}: {m}", "danger")

    return render_template("event_new.html", form=form)

# VERSION 3 START
# Show all events created by the logged-in organiser
@bp.route("/organiser/events")
def organiser_events():
    # Restrict access to organisers only
    guard = require_role(ROLE_ORG)
    if guard:
        return guard
    
    # Restrict access to organisers only
    org = Organiser.query.filter_by(user_id=current_user.id).first()
    if not org:
        flash("No organiser profile linked to your account.", "warning")
        return redirect(url_for("main.index"))

    # Fetch only events created by this organiser
    events = (
        Event.query
        .filter_by(organiser_id=org.id)
        .order_by(Event.created_at.desc())
        .all()
    )
    # Render organiser events page
    return render_template("organiser_events.html", events=events, org=org)

# Edit an existing event owned by the organiser
@bp.route("/organiser/events/<int:event_id>/edit", methods=["GET", "POST"])
def organiser_event_edit(event_id):
    # Restrict access to organisers only
    guard = require_role(ROLE_ORG)
    if guard:
        return guard

    # Fetch event and verify organiser ownership
    ev, org = _get_event_for_current_organiser_or_404(event_id)
    # Initialise the event form
    form = EventForm()

    # Fetch only verified charities for beneficiary selection
    verified_charities = Charity.query.filter_by(verified=True).order_by(Charity.name.asc()).all()
    charity_choices = [(c.id, c.name) for c in verified_charities]

    # Populate form fields when loading the page
    if request.method == "GET":
        form.title.data = ev.title
        form.description.data = ev.description
        form.venue.data = ev.venue
        form.starts_at.data = ev.starts_at
        form.ticket_price_eur.data = (ev.ticket_price_cents or 0) / 100
        form.published.data = bool(ev.published)

        # Reset beneficiary entries
        form.beneficiaries.entries = []
        form.beneficiaries.min_entries = 0

        # Populate beneficiaries from existing event data
        existing = ev.beneficiaries or []
        if not existing:
            form.beneficiaries.append_entry()
        else:
            for b in existing:
                entry = form.beneficiaries.append_entry()
                entry.form.charity_id.data = b.charity_id
                entry.form.allocation_percent.data = b.allocation_percent
    
    # Apply charity choices to each beneficiary row
    for b in form.beneficiaries:
        b.form.charity_id.choices = charity_choices

    # Add a new beneficiary row without saving the form
    if request.method == "POST" and "add_beneficiary" in request.form:
        form.beneficiaries.append_entry()
        for b in form.beneficiaries:
            b.form.charity_id.choices = charity_choices
        return render_template("organiser_event_edit.html", form=form, ev=ev)

    # Save changes when form is submitted
    if form.validate_on_submit():
        # Ensure beneficiary allocations total 100%
        total_alloc = sum((b.form.allocation_percent.data or 0) for b in form.beneficiaries)
        if total_alloc != 100:
            flash("Allocation must total 100%.", "danger")
            return render_template("organiser_event_edit.html", form=form, ev=ev)

        # Update event fields
        ev.title = form.title.data.strip()
        ev.description = form.description.data.strip() if form.description.data else ""
        ev.venue = form.venue.data.strip() if form.venue.data else ""
        ev.starts_at = form.starts_at.data
        ev.ticket_price_cents = cents(form.ticket_price_eur.data)
        ev.published = bool(form.published.data)

        # Remove existing beneficiaries
        EventBeneficiary.query.filter_by(event_id=ev.id).delete()
        db.session.flush()

        # Add updated beneficiaries
        for b in form.beneficiaries:
            db.session.add(EventBeneficiary(
                event_id=ev.id,
                charity_id=b.form.charity_id.data,
                allocation_percent=b.form.allocation_percent.data
            ))

        # Save changes to the database
        db.session.commit()
        flash("Event updated.", "success")
        return redirect(url_for("main.organiser_events"))

    # Display validation errors
    if request.method == "POST":
        for field, msgs in form.errors.items():
            for m in msgs:
                flash(f"{field}: {m}", "danger")
    # Render edit page
    return render_template("organiser_event_edit.html", form=form, ev=ev)

# Show analytics for a specific organiser-owned event
@bp.route("/organiser/events/<int:event_id>/analytics")
@login_required
def organiser_event_analytics(event_id):
    # Restrict access to organisers only
    guard = require_role(ROLE_ORG)
    if guard:
        return guard

    # Fetch event and verify organiser ownership
    ev, org = _get_event_for_current_organiser_or_404(event_id)

    # Query only paid orders for this event
    paid_orders_q = Order.query.filter_by(event_id=ev.id, status="PAID")
    # Count number of paid orders
    paid_orders_count = paid_orders_q.count()
    # Calculate totals using SQL aggregation
    totals = paid_orders_q.with_entities(
        func.coalesce(func.sum(Order.qty), 0),
        func.coalesce(func.sum(Order.total_cents), 0),
        func.coalesce(func.sum(Order.donation_cents), 0),
    ).first()
    # Extract totals
    tickets_sold = int(totals[0] or 0)
    total_raised_cents = int(totals[1] or 0)
    donation_total_cents = int(totals[2] or 0)
    # Calculate average order value
    avg_order_cents = int(total_raised_cents / paid_orders_count) if paid_orders_count else 0

    # Estimate beneficiary allocations based on percentages
    allocations = []
    for b in ev.beneficiaries:
        allocations.append({
            "charity_name": b.charity.name if b.charity else "Unknown charity",
            "percent": b.allocation_percent,
            "estimated_cents": int(round((total_raised_cents * (b.allocation_percent or 0)) / 100)),
        })
    # Render analytics page
    return render_template(
        "organiser_event_analytics.html",
        ev=ev,
        paid_orders_count=paid_orders_count,
        tickets_sold=tickets_sold,
        total_raised_cents=total_raised_cents,
        donation_total_cents=donation_total_cents,
        avg_order_cents=avg_order_cents,
        allocations=allocations,
    )

# VERSION 3 END

# VERSION 1