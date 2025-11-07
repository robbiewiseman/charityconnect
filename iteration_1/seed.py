# Version 1

import os
import datetime as dt
from app import create_app
from models import db, User, Organiser, Charity, Event, EventBeneficiary, Order, Ticket, ROLE_USER, ROLE_ORG, ROLE_ADMIN

app = create_app()

def cents(euro):
    return int(round(euro * 100))

def seed():
    # Reference: Flask application context (Pallets Projects, 2024)
    # https://flask.palletsprojects.com/en/stable/appcontext/
    with app.app_context():
        db.drop_all()
        db.create_all()

        # USERS
        admin = User(email="admin@example.com", name="Admin", role=ROLE_ADMIN)
        admin.set_password("admin123")

        organiser_user = User(email="organiser@example.com", name="Cork Charity Org", role=ROLE_ORG)
        organiser_user.set_password("organiser123")

        user = User(email="user@example.com", name="Demo User", role=ROLE_USER)
        user.set_password("user123")

        db.session.add_all([admin, organiser_user, user])
        # Reference: SQLAlchemy session commit pattern (SQLAlchemy, 2024)
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html
        db.session.commit()

        # ORGANISER PROFILE
        organiser_profile = Organiser(
            user_id=organiser_user.id,
            organisation_name="Cork Community Fundraisers",
            charity_number="CHY98765",
            verified=True
        )
        db.session.add(organiser_profile)

        # CHARITIES
        c1 = Charity(name="Irish Cancer Society", regulator_ref="CHY5863")
        c2 = Charity(name="Pieta", regulator_ref="20062026")
        c3 = Charity(name="Focus Ireland", regulator_ref="CHY7220")
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        # EVENTS
        e1 = Event(
            organiser_id=organiser_profile.id,
            title="Christmas Charity Gala",
            description="Annual Christmas fundraising dinner with live music and raffle.",
            venue="Cork City Hall",
            starts_at=dt.datetime.utcnow() + dt.timedelta(days=14),
            ticket_price_cents=cents(50),
            published=True
        )
        e2 = Event(
            organiser_id=organiser_profile.id,
            title="Community 5K Fun Run",
            description="Join our 5K charity run to support local shelters.",
            venue="Fitzgerald Park, Cork",
            starts_at=dt.datetime.utcnow() + dt.timedelta(days=30),
            ticket_price_cents=cents(10),
            published=True
        )
        db.session.add_all([e1, e2])
        db.session.flush()

        # BENEFICIARIES
        db.session.add(EventBeneficiary(event_id=e1.id, charity_id=c1.id, allocation_percent=60))
        db.session.add(EventBeneficiary(event_id=e1.id, charity_id=c2.id, allocation_percent=40))
        db.session.add(EventBeneficiary(event_id=e2.id, charity_id=c3.id, allocation_percent=100))

        db.session.commit()

        # ORDERS / TICKETS / RECEIPTS (Demo)
        order1 = Order(
            event_id=e1.id,
            user_id=user.id,
            email=user.email,
            qty=2,
            donation_cents=cents(10),
            total_cents=e1.ticket_price_cents * 2 + cents(10),
            status="PAID",
        )
        db.session.add(order1)
        db.session.flush()

        # tickets
        t1 = Ticket(order_id=order1.id, code=f"T{order1.id:06d}-01")
        t2 = Ticket(order_id=order1.id, code=f"T{order1.id:06d}-02")
        db.session.add_all([t1, t2])

        db.session.commit()

        print("Seed complete.")
        print("Accounts:")
        print(" - Admin:     admin@example.com / admin123")
        print(" - Organiser: organiser@example.com / organiser123")
        print(" - User:      user@example.com / user123")
        print("Events:")
        print(" - Christmas Charity Gala")
        print(" - Community 5K Fun Run")

if __name__ == "__main__":
    seed()
# Version 1