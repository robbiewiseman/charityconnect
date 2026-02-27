# VERSION 1
============================================================
CharityConnect – Final Year Project (BIS, University College Cork)
Student: Robert Wiseman (122436052)
============================================================
PROJECT OVERVIEW
------------------------------------------------------------
CharityConnect is a Flask-based fundraising platform that enables event organisers to create and manage charity events, issue digital tickets, and generate verified receipts with QR codes for attendees. The system is designed to demonstrate a Proof-of-Value artefact by improving transparency, usability, and affordability in charitable event management.

The system has three primary user roles:
 - Donor/User: Can browse and purchase tickets for charity events.
 - Organiser: Can create and manage charity events and beneficiaries.
 - Administrator: Can verify organiser accounts and audit event activity.
------------------------------------------------------------
ENVIRONMENT AND SETUP
------------------------------------------------------------
Developed using:
 - Python 3.14
 - Flask 3.0
 - SQLAlchemy ORM
 - Flask-WTF (CSRF protection and form validation)
 - PostgreSQL (via Neon cloud instance)

Local environment managed using:
 - `python-dotenv` for .env configuration
 - `virtualenv` for package isolation
 - `pip install -r requirements.txt` for dependency setup
------------------------------------------------------------
DATABASE CONNECTION
------------------------------------------------------------
The system connects to a Neon PostgreSQL database hosted at: postgresql://neondb_owner@ep-orange-wildflower-abcvb0ut-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require
A local SQLite fallback (`local.db`) is used if no Neon connection is available.
Environment variables are stored in `.env` and loaded at runtime.
------------------------------------------------------------
INSTALLATION AND EXECUTION
------------------------------------------------------------
1. Open the project in VS Code or a terminal.
2. Delete, create, and activate a virtual environment:
       rmdir -Recurse -Force .venv 2>$null
       python -m venv .venv
       .\.venv\Scripts\activate
3. Install dependencies:
       pip install -r requirements.txt
4. Run the application:
       python app.py
5. Access locally:
       http://127.0.0.1:5000
------------------------------------------------------------
VERSION CONTROL
------------------------------------------------------------
All code files contain version comments (e.g. Version 1). Future iterations will increment these to 2, 3, etc. Version control is maintained locally through manual version tagging, and also through a GitHub Repository.
============================================================
# VERSION 1