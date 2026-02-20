# VERSION 1

# This file defines all the forms used in the CharityConnect web application.
# Each form handles user input and validation for specific parts of the system.

from flask_wtf import FlaskForm
# VERSION 5 START
from flask_wtf.file import FileField, FileAllowed
# VERSION 5 END
from wtforms import (StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField, BooleanField, DateTimeLocalField, DecimalField, FieldList, FormField, EmailField)
# VERSION 3 START
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, Optional, InputRequired
# VERSION 3 END

# User registration form
class RegisterForm(FlaskForm):
    # basic user details
    # Reference: WTForms validators (WTForms, 2024)
    # https://wtforms.readthedocs.io/en/stable/validators/
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    # Reference: Flask-WTF/WTForms password + confirmation (WTForms, 2024)
    # https://wtforms.readthedocs.io/en/stable/validators/
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirm", validators=[DataRequired(), EqualTo('password')])

    # optional organiser-specific fields
    as_organiser = BooleanField("Register as organiser?")
    org_name = StringField("Organisation Name", validators=[Optional(), Length(max=200)])
    charity_number = StringField("Charity Number", validators=[Optional(), Length(max=100)])

    # VERSION 3 START
    consent = BooleanField(
        "I agree to the Terms and Privacy Policy",
        validators=[InputRequired(message="You must agree before registering.")]
    )
    # VERSION 3 END

    # form submission
    submit = SubmitField("Register")

# Login form
class LoginForm(FlaskForm):
    # Used for logging in existing users
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# Event Creation Form
class BeneficiaryForm(FlaskForm):
    # Used inside EventForm to assign charity beneficiaries and their percentage allocations
    charity_id = SelectField("Charity", coerce=int, validators=[DataRequired()])
    allocation_percent = IntegerField("% Allocation", validators=[DataRequired(), NumberRange(min=1, max=100)])

# Event creation form
class EventForm(FlaskForm):
    # Used for organisers to create and publish charity event
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=4000)])
    venue = StringField("Venue", validators=[Optional(), Length(max=200)])
    # Reference: using datetime-local format with WTForms (rendered in template) (WTForms crash course)
    # https://wtforms.readthedocs.io/en/stable/crash_course/#rendering-fields
    starts_at = DateTimeLocalField("Starts At", validators=[DataRequired()], format="%Y-%m-%dT%H:%M")
    # Reference: DecimalField + numeric validation (WTForms, 2024)
    # https://wtforms.readthedocs.io/en/stable/fields/
    ticket_price_eur = DecimalField("Ticket Price (€)", places=2, rounding=None, validators=[DataRequired(), NumberRange(min=0)])
    published = BooleanField("Publish?")
    # VERSION 5 START
    cover_image = FileField("Event Image (optional)", validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'JPG and PNG only.')
    ])
    # VERSION 5 END

    # allow organisers to add multiple charities to an event
     # Reference: FieldList + FormField composition (WTForms, 2024)
    # https://wtforms.readthedocs.io/en/stable/fields/
    beneficiaries = FieldList(FormField(BeneficiaryForm), min_entries=1, max_entries=5)
    submit = SubmitField("Save Event")

# Ticket purchase form
class PurchaseForm(FlaskForm):
    # Used by donors to buy tickets and optionally add a donation
    email = StringField("Email", validators=[DataRequired(), Email()])
    qty = IntegerField("Tickets", default=1, validators=[DataRequired(), NumberRange(min=1, max=10)])
    donation_eur = DecimalField("Optional Donation (€)", default=0, places=2, validators=[NumberRange(min=0)])
    # VERSION 3 START
    consent = BooleanField(
        "I consent to my data being used to process this order",
        validators=[InputRequired(message="You must consent before checkout.")]
    )
    # VERSION 3 END
    # Reference: Flask-WTF CSRF hidden tag used in templates via FlaskForm (Pallets Projects, 2024)
    # https://flask-wtf.readthedocs.io/en/1.2.x/form/
    submit = SubmitField("Confirm Order")

# VERSION 2 START
class ApplyVerificationForm(FlaskForm):
    # Whether the applicant is an event organiser or a registered charity
    org_type = SelectField(
        "I am applying as",
        choices=[("organiser", "Organiser"), ("charity", "Charity")],
        validators=[DataRequired()]
    )
    # Name of the organisation applying for verification
    organisation_name = StringField("Organisation Name", validators=[DataRequired()])
    # Optional charity registration number (only relevant for charities)
    charity_number = StringField("Charity Number (optional)")
    # Main contact email for verification follow-up
    contact_email = EmailField("Contact Email", validators=[DataRequired(), Email()])
    # Submit button for the verification request
    submit = SubmitField("Submit Application")
# VERSION 2 END

# VERSION 3 START
class AccountForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=320)])
    marketing_consent = BooleanField("I want to receive product updates and marketing emails")
    submit = SubmitField("Save changes")

# VERSION 3 END

# VERSION 1