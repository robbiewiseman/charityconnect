# VERSION 1

This document lists all external documentation, frameworks, and official libraries referenced in the design and implementation of the CharityConnect system. All referenced sources are publicly available and used solely to 
support the creation of original code for my CharityConnect project.

Each source below identifies where its concepts or code patterns were applied and includes direct in-code comments to maintain traceability for audit purposes.


1. Flask Documentation (Pallets Projects, 2024)
URLs:
https://flask.palletsprojects.com/en/stable/
https://flask.palletsprojects.com/en/stable/patterns/appfactories/
https://flask.palletsprojects.com/en/stable/blueprints/
https://flask.palletsprojects.com/en/stable/tutorial/views/
https://flask.palletsprojects.com/en/stable/config/
Usage:
app.py: Application factory structure (`create_app()`), environment configuration, and extension initialisation.
routes.py: Blueprint registration, route definitions, and use of decorators.
config.py: Configuration object pattern for environment variables and security keys.
seed.py: Use of `app.app_context()` for database initialisation and shell context access.
forms.py: Form structure and CSRF protection integrated through Flask-WTF (extension documented within Flask).
Notes: The Flask documentation guided the structural design of the web application, including the modular app factory setup, Blueprint routing system, and integration of extensions (CSRF, database, and mail). All framework-level logic was written independently following official Flask conventions.


2. SQLAlchemy 2.0 Documentation (SQLAlchemy, 2024)
URLs: 
https://docs.sqlalchemy.org/en/20/
https://docs.sqlalchemy.org/en/20/orm/quickstart.html
https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
https://docs.sqlalchemy.org/en/20/orm/relationship_api.html
https://docs.sqlalchemy.org/en/20/orm/session_basics.html
https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html
https://docs.sqlalchemy.org/en/20/core/engines.html
Usage:
models.py: Model definitions, relationships, and ORM cascade patterns.
routes.py: Querying, filtering, and session commits.
seed.py: Database initialisation and session handling.
app.py: Integration of SQLAlchemy with Flask app factory.
Notes: SQLAlchemy’s ORM layer was used for all model relationships, cascade deletes, and session operations. These patterns were adapted from the official 2.0 documentation and tailored for the CharityConnect schema.


3. Flask-WTF Documentation (Pallets Projects, 2024)
URLs: 
https://flask-wtf.readthedocs.io/en/1.2.x/
https://flask-wtf.readthedocs.io/en/1.2.x/quickstart/
https://flask-wtf.readthedocs.io/en/1.2.x/csrf/
https://flask-wtf.readthedocs.io/en/1.2.x/form/
Usage:
forms.py: Implementation of secure web forms using FlaskForm subclasses, field validation, and CSRF integration.
routes.py: Handling POST form submissions, validation errors, and redirects upon successful submission.
app.py / extensions.py: Configuration of global CSRF protection via CSRFProtect extension.
Notes:
The Flask-WTF documentation provided direct guidance for form class creation, validator integration, and secure CSRF handling.
These patterns were adapted and extended for event creation, organiser verification, and ticket purchase forms throughout the CharityConnect system.


4. Werkzeug Security Utilities (Pallets Projects, 2024)
URLs: 
https://werkzeug.palletsprojects.com/en/stable/utils/
https://werkzeug.palletsprojects.com/en/stable/utils/#werkzeug.security.generate_password_hash
https://werkzeug.palletsprojects.com/en/stable/utils/#werkzeug.security.check_password_hash
https://werkzeug.palletsprojects.com/en/stable/utils/#module-werkzeug.security
Usage:
models.py: Implementation of password hashing and verification using `generate_password_hash()` and `check_password_hash()` methods within the User model.
Notes: Werkzeug’s official security utilities were referenced to ensure secure password storage and verification, following industry-standard cryptographic practices. This ensures compliance with Flask’s recommended approach for password protection in production-ready web applications.


5. Neon Serverless Postgres Documentation (Neon Tech, 2025) and PostgreSQL Documentation (PostgreSQL Global Development Group, 2025)
URLs:
https://neon.com/docs/
https://neon.com/docs/connect/connect-from-any-app
https://neon.com/docs/local/neon-local#environment-variables-and-configuration-options
https://neon.com/docs/connect/connect-securely
https://www.postgresql.org/docs/
https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
https://www.postgresql.org/docs/current/libpq-envars.html
Usage:
app.py: Cloud PostgreSQL database connection using SSL mode (`sslmode=require`).
config.py: Environment variable configuration for `DATABASE_URL` and fallback to local SQLite.
.env: Connection string format adapted from Neon’s official connection guide.
Notes: The Neon and PostgreSQL documentation informed the secure connection setup for the cloud-hosted database. Environment variables and SSL enforcement were configured based on best practices from Neon’s developer guide and PostgreSQL’s official connection specifications.


6. Jinja Template Documentation (Pallets Projects, 2024)
URLs: 
https://jinja.palletsprojects.com/en/stable/templates/
https://jinja.palletsprojects.com/en/stable/templates/#template-inheritance
https://jinja.palletsprojects.com/en/stable/templates/#list-of-control-structures
https://jinja.palletsprojects.com/en/stable/templates/#variables
https://jinja.palletsprojects.com/en/stable/templates/#filters
Usage:
base.html: Template inheritance using {% extends %} and {% block content %} to define the master layout.
index.html, event_new.html, event_detail.html, event_buy.html, admin_verify.html: Jinja syntax for conditional rendering ({% if ... %}), iteration ({% for ... %}), and variable interpolation ({{ ... }}).
Notes: The Jinja documentation guided the templating logic and structure used across all HTML files. Each page extends base.html and uses Jinja control flow to render dynamic data passed from Flask routes. The syntax was implemented independently following official Jinja conventions for reusable and maintainable templates.


7. Flask URL Building Documentation (Pallets Projects, 2024)
URL: https://flask.palletsprojects.com/en/stable/quickstart/#url-building
Usage:
base.html: Dynamic navigation links (url_for('main.index'), url_for('main.admin_verify'), etc.).
event_detail.html, event_buy.html, event_new.html: Used for POST form actions and route redirections.
Notes: Flask’s URL building feature ensures that routes remain dynamic and maintainable, avoiding hard-coded links. The implementation in CharityConnect follows Flask’s official guidance for clean, blueprint-based routing.


8. Flask-WTF and WTForms Documentation (Pallets Projects, 2024; WTForms, 2024)
URLs:
https://flask-wtf.readthedocs.io/en/1.2.x/
https://flask-wtf.readthedocs.io/en/1.2.x/quickstart/
https://flask-wtf.readthedocs.io/en/1.2.x/csrf/
https://flask-wtf.readthedocs.io/en/1.2.x/form/
https://wtforms.readthedocs.io/en/stable/
https://wtforms.readthedocs.io/en/stable/fields/
https://wtforms.readthedocs.io/en/stable/validators/
https://wtforms.readthedocs.io/en/stable/crash_course/
Usage:
forms.py: Integration of FlaskForm subclasses with WTForms field types and validators for input handling.
event_new.html, event_buy.html: Use of form.hidden_tag() for CSRF tokens, dynamic field rendering, and inline validation error display.
routes.py: Handling POST submissions and validating FlaskForm instances before committing data.
Notes: These documents guided the secure and modular form architecture used throughout CharityConnect. Flask-WTF provided the Flask integration layer for CSRF and validation, while WTForms documentation informed the underlying field, validator, and template rendering patterns.

9. CSRF Protection Documentation (Pallets Projects, 2024)
URL: https://flask-wtf.readthedocs.io/en/1.2.x/api/?highlight=csrf#module-flask_wtf.csrf
Usage:
admin_verify.html, event_new.html, event_buy.html: Inclusion of hidden CSRF tokens via {{ csrf_token() }} and {{ form.hidden_tag() }} in all POST forms.
extensions.py: Integration of CSRFProtect extension with the Flask application.
Notes: The CSRF protection guidelines from Flask-WTF were implemented to secure all user interactions involving POST requests, maintaining best practices for web application security.


10. Python Datetime Module (Python Software Foundation, 2024)
URL: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
Usage:
event_detail.html, event_buy.html, order_details.html: Formatting event timestamps using .strftime('%Y-%m-%d %H:%M') for readable date-time display.
Notes: Datetime formatting from the Python standard library was used to convert stored timestamps into a user-friendly format across all event-related templates.


11. HTML5 Input Type Documentation (Mozilla Developer Network, 2024)
URL: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/datetime-local
Usage:
event_new.html: Implemented <input type="datetime-local"> for capturing event start times with proper client-side validation.
Notes: The MDN documentation informed the use of semantic and accessible HTML5 input elements to enhance form usability and validation in modern browsers.


12. HTML Table & Accessibility Guidelines (Mozilla Developer Network, 2024)
URLs:
https://developer.mozilla.org/en-US/docs/Learn/HTML/Tables/Basics
https://developer.mozilla.org/en-US/docs/Learn/Accessibility/HTML
Usage:
admin_verify.html: Use of <table>, <thead>, <tbody>, and <th> elements to present organiser data with semantic structure.
Notes: MDN documentation guided the markup and accessibility structure for admin data tables, ensuring proper semantics for assistive technologies and responsive layouts.


13. Bootstrap 5 Documentation (Bootstrap, 2024)
URL: https://getbootstrap.com/docs/5.3/getting-started/introduction/
Usage:
order_details.html: Utilised layout classes (row, col-lg-8, shadow-sm, border-0) to create a clean confirmation page layout.
Notes: Bootstrap utility classes were selectively used for responsive grid alignment and spacing. The project does not depend on Bootstrap JavaScript—only structural and styling utilities were referenced.

14. ChatGPT usage:

CSS: https://chatgpt.com/share/690e2571-05ec-8004-8017-1c480e7546dd
Routes.py: https://chatgpt.com/share/690df926-fc70-8004-8452-e99ab50a799c
Models.py: https://chatgpt.com/share/690dfb57-a0a0-8004-8d11-cfb295a3e904

# VERSION 1