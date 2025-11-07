# VERSION 1

# Reference: routes.py was adapted from this ChatGPT template: https://chatgpt.com/share/690df926-fc70-8004-8452-e99ab50a799c

# This file defines all routes (URLs) and views for the CharityConnect application.
# It includes routes for public users, organisers, and admins.
# Each route connects frontend templates with backend database logic.

from flask import (Blueprint, render_template, redirect, url_for, request, flash, abort, session)
from flask_mail import Mail
from extensions import csrf

from models import (db, User, Organiser, Charity, Event, EventBeneficiary, Order, Ticket, ROLE_USER, ROLE_ORG, ROLE_ADMIN)

# Reference: Flask Blueprints Documentation (Pallets Projects, 2024)
# https://flask.palletsprojects.com/en/stable/blueprints/
# Create a Flask Blueprint for routing
bp = Blueprint("main", __name__)
mail = Mail()

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

# Utility Function
def cents(eur_decimal):
    return int(round(float(eur_decimal or 0) * 100))

# Template Processor
@bp.app_context_processor
def inject_current_role():
    # Makes the current role available in all templates (for navigation display)
    return {"current_role": get_role()}

# Role switching
@bp.route("/role/<role>")
def switch_role(role):
    # Allows easy switching between roles for testing/admin purposes
    set_role(role)
    flash(f"Role switched to: {get_role()}", "info")
    return redirect(url_for("main.index"))

# Public Routes
@bp.route("/")
def index():
    # Display all published charity events on the homepage
    # Reference: SQLAlchemy Query Guide – filtering and ordering (SQLAlchemy, 2024)
    # https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html
    events = Event.query.filter_by(published=True).order_by(Event.starts_at.asc()).all()
    return render_template("index.html", events=events)

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
    from forms import PurchaseForm
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
            email=form.email.data.lower(),
            qty=qty,
            donation_cents=donation_c,
            total_cents=total_c,
            status="PAID",
        )
        db.session.add(order)
        db.session.flush()

         # Generate ticket records for each quantity
        for i in range(qty):
            db.session.add(Ticket(order_id=order.id, code=f"T{order.id:06d}-{i+1:02d}"))

        # Reference: SQLAlchemy session commit (SQLAlchemy, 2024)
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html
        db.session.commit()
        
        flash("Order completed. You can download your receipt now.", "success")
        return redirect(url_for('main.order_detail', order_id=order.id))

    # Handle validation errors
    if request.method == "POST":
        for field, msgs in form.errors.items():
            for m in msgs:
                flash(f"{field}: {m}", "danger")

    return render_template("event_buy.html", ev=ev, form=form)

@bp.route("/orders/<int:order_id>")
# Show order confirmation and details
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("order_detail.html", order=order)

# Admin Routes
@bp.route("/admin/verify")
def admin_verify():
    guard = require_role(ROLE_ADMIN)
    if guard:
        return guard
    # Admin view to verify or unverify organisers
    orgs = Organiser.query.order_by(Organiser.verified.asc(), Organiser.id.desc()).all()
    return render_template("admin_verify.html", orgs=orgs)

@bp.route("/admin/verify/<int:org_id>/toggle", methods=["POST"])
# Reference: CSRF API (disabled here for demo only) (Pallets Projects, 2024)
# https://flask-wtf.readthedocs.io/en/1.2.x/csrf/
@csrf.exempt  # CSRF disabled for simplicity in admin toggle (use with care)
def admin_toggle_verify(org_id):
    guard = require_role(ROLE_ADMIN)
    if guard:
        return guard
    # Toggle organiser verification status
    org = Organiser.query.get_or_404(org_id)
    org.verified = not org.verified
    db.session.commit()
    flash(f"Organiser {'verified' if org.verified else 'unverified'}.", "success")
    return redirect(url_for('main.admin_verify'))

# Organiser Routes
@bp.route("/organiser/events/new", methods=["GET","POST"])
def event_new():
    guard = require_role(ROLE_ORG, ROLE_ADMIN)
    if guard:
        return guard
    # Allow organisers to create and publish charity events
    from forms import EventForm
    form = EventForm()
    charities = Charity.query.order_by(Charity.name.asc()).all()
    for bf in form.beneficiaries:
        bf.form.charity_id.choices = [(c.id, c.name) for c in charities]

    # Add extra beneficiary rows dynamically
    if request.method == "POST" and "add_beneficiary" in request.form:
        form.beneficiaries.append_entry()
        for bf in form.beneficiaries:
            bf.form.charity_id.choices = [(c.id, c.name) for c in charities]
        return render_template("event_new.html", form=form)

    # Validate and save new event
    if form.validate_on_submit():
        total_alloc = sum(b.form.allocation_percent.data or 0 for b in form.beneficiaries)
        if total_alloc != 100:
            flash("Allocation must total 100%.", "danger")
            return render_template("event_new.html", form=form)

        # Create organiser (for testing/demo if none exist)
        org = Organiser.query.first()
        if not org:
            org = Organiser(organisation_name="Iteration Organiser", charity_number="ITER-000", verified=True)
            db.session.add(org); db.session.flush()

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
        db.session.add(ev); db.session.flush()

        # Add beneficiary allocations
        for b in form.beneficiaries:
            db.session.add(EventBeneficiary(
                event_id=ev.id,
                charity_id=b.form.charity_id.data,
                allocation_percent=b.form.allocation_percent.data
            ))
        
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