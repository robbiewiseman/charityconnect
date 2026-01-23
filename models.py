# VERSION 1

# Reference: models.py code was adapted based off this ChatGPT template: https://chatgpt.com/share/690dfb57-a0a0-8004-8d11-cfb295a3e904

# This file defines all database models (tables) used in the CharityConnect system.
# Each class represents a table in the database using SQLAlchemy ORM.

import datetime as dt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
# VERSION 2 START
from sqlalchemy import LargeBinary
from datetime import datetime
# VERSION 2 END

# Reference: Werkzeug Security Utilities (Pallets Projects, 2024)
# https://werkzeug.palletsprojects.com/en/stable/utils/#werkzeug.security.generate_password_hash
from werkzeug.security import generate_password_hash, check_password_hash

# Initialise SQLAlchemy for database connection and model management
db = SQLAlchemy()

# Define simple constants for user roles
ROLE_USER = "user"
ROLE_ORG = "organiser"
ROLE_ADMIN = "admin"

# User
class User(UserMixin, db.Model):
    # Stores login and profile details for all users (admins, organisers, donors)
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(320), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), default=ROLE_USER, nullable=False)
    name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    # VERSION 3 START
    marketing_consent = db.Column(db.Boolean, nullable=False, default=False)
    marketing_consent_at = db.Column(db.DateTime, nullable=True)
    marketing_consent_withdrawn_at = db.Column(db.DateTime, nullable=True)

    consent_registered_at = db.Column(db.DateTime, nullable=True)
    # VERSION 3 END

    # Relationship: one user can be linked to one organiser profile
    organiser = db.relationship('Organiser', backref='user', uselist=False)

    # Set and check password methods (for secure authentication)
    # Reference: Werkzeug password hashing & verification (Pallets Projects, 2024)
    # https://werkzeug.palletsprojects.com/en/stable/utils/#werkzeug.security.generate_password_hash
    # https://werkzeug.palletsprojects.com/en/stable/utils/#werkzeug.security.check_password_hash
    def set_password(self, raw): 
        self.password_hash = generate_password_hash(raw)
    def check_password(self, raw): 
        return check_password_hash(self.password_hash, raw)

# Organiser
class Organiser(db.Model):
    # Represents an event organiser verified by the platform
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=True)
    organisation_name = db.Column(db.String(200))
    charity_number = db.Column(db.String(100))
    # VERSION 2 START
    # store whether they applied as an organiser or a charity
    org_type = db.Column(db.String(20), nullable=False, default="organiser")
    # Verification workflow
    status = db.Column(db.String(20), nullable=False, default="pending")
    verified = db.Column(db.Boolean, nullable=False, default=False)
    # Contact details used in the Apply form
    contact_name = db.Column(db.String(120))
    contact_email = db.Column(db.String(320))
    website_url = db.Column(db.String(255))
    # VERSION 2 END

# Charity
class Charity(db.Model):
    # Represents registered charities that can receive funds
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    # VERSION 2 START
    charity_number = db.Column(db.String(100))
    contact_email = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default="pending")
    verified = db.Column(db.Boolean, nullable=False, default=False)
    # VERSION 2 END

# Event
class Event(db.Model):
    # Represents a fundraising event created by an organiser
    id = db.Column(db.Integer, primary_key=True)
    organiser_id = db.Column(db.Integer, db.ForeignKey('organiser.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    venue = db.Column(db.String(200))
    starts_at = db.Column(db.DateTime, nullable=False)
    published = db.Column(db.Boolean, default=False)
    ticket_price_cents = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

    # Relationships to organiser and beneficiaries
    organiser = db.relationship('Organiser', backref='events')
    # Reference: SQLAlchemy relationships + cascade delete (SQLAlchemy, 2024)
    # https://docs.sqlalchemy.org/en/20/orm/relationship_api.html
    # https://docs.sqlalchemy.org/en/20/orm/cascades.html
    beneficiaries = db.relationship('EventBeneficiary', backref='event', cascade="all, delete-orphan")

# Event Beneficiaries
class EventBeneficiary(db.Model):
    # Links events to one or more charities with allocation percentages
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), index=True)
    charity_id = db.Column(db.Integer, db.ForeignKey('charity.id'))
    allocation_percent = db.Column(db.Integer, nullable=False)

    # Relationship to the Charity model
    # Reference: relationship to another mapped class (SQLAlchemy, 2024)
    # https://docs.sqlalchemy.org/en/20/orm/relationship_api.html
    charity = db.relationship('Charity')

# Order
class Order(db.Model):
    # Stores ticket purchases and donations made by users
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    email = db.Column(db.String(320), nullable=False)
    qty = db.Column(db.Integer, default=1)
    donation_cents = db.Column(db.Integer, default=0)
    total_cents = db.Column(db.Integer, default=0)
    # VERSION 2 START
    status = db.Column(db.String(32), default='PENDING')
    stripe_payment_intent = db.Column(db.String(100), index=True)
    receipt_pdf = db.Column(LargeBinary, nullable=True)
    # VERSION 2 END
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # VERSION 3 START
    consent_checkout_at = db.Column(db.DateTime, nullable=True)
    consent_checkout_ip = db.Column(db.String(64), nullable=True)
    consent_checkout_ua = db.Column(db.String(255), nullable=True)
    # VERSION 3 END

    # Relationships to other tables
    event = db.relationship('Event')
    user = db.relationship('User')
    # Reference: one-to-many with cascade (tickets) (SQLAlchemy, 2024)
    # https://docs.sqlalchemy.org/en/20/orm/relationship_api.html
    tickets = db.relationship('Ticket', backref='order', cascade="all, delete-orphan", lazy='dynamic')

# Ticket
class Ticket(db.Model):
    # Represents an individual ticket generated from an order
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), index=True)
    code = db.Column(db.String(40), unique=True, index=True)
    redeemed = db.Column(db.Boolean, default=False)

# VERSION 1