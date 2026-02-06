# VERSION 1
====================================================================================

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
# VERSION 2 START 
https://flask.palletsprojects.com/en/stable/templating/#context-processors
Usage:
app.py: Application factory structure (`create_app()`), environment configuration, and extension initialisation.
routes.py: Blueprint registration, route definitions, use of decorators, and use of context processors to inject global variables into templates.
config.py: Configuration object pattern for environment variables and security keys.
seed.py: Use of `app.app_context()` for database initialisation and shell context access.
forms.py: Form structure and CSRF protection integrated through Flask-WTF (extension documented within Flask).
Templates: Use of context processors to expose helper values globally.
Notes: The Flask documentation guided the structural design of the web application, including the modular app factory setup, Blueprint routing system, context processors, and integration of extensions (CSRF, database, and mail). All framework-level logic was written independently following official Flask conventions.
# VERSION 2 END


2. SQLAlchemy 2.0 Documentation (SQLAlchemy, 2024)
URLs: 
https://docs.sqlalchemy.org/en/20/
https://docs.sqlalchemy.org/en/20/orm/quickstart.html
https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
https://docs.sqlalchemy.org/en/20/orm/relationship_api.html
https://docs.sqlalchemy.org/en/20/orm/session_basics.html
https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html
https://docs.sqlalchemy.org/en/20/core/engines.html
# VERSION 2 START
https://docs.sqlalchemy.org/en/20/core/connections.html#engine-disposal
Usage:
models.py: Model definitions, relationships, and ORM cascade patterns.
routes.py: Querying, filtering, and session commits.
seed.py: Database initialisation and session handling.
app.py: Integration of SQLAlchemy with Flask app factory.
Iteration 2: Engine disposal/reconnect pattern used to improve connection stability (especially with Neon and webhook processing).
Notes: SQLAlchemy’s ORM layer was used for all model relationships, cascade deletes, session operations, and engine disposal patterns. These patterns were adapted from the official 2.0 documentation and tailored for the CharityConnect schema.
# VERSION 2 END


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
# VERSION 2 START 
receipt builder in routes.py: https://chatgpt.com/share/691d0c58-b260-8004-8756-d6215df38da4
# VERSION 2 END
# VERSION 3 START
JavaScript Logic in event_new.html and organiser_event_analytics.html: https://chatgpt.com/share/69736e29-4d08-8004-a8ff-71f40f533a51
# VERSION 3 END

====================================================================================
# VERSION 1
====================================================================================

# VERSION 2 START
====================================================================================


15. Stripe Webhooks & Checkout Documentation (Stripe, 2025)
URLs:
https://docs.stripe.com/webhooks/quickstart?lang=python
https://docs.stripe.com/testing
https://docs.stripe.com/api/checkout/sessions/create
https://docs.stripe.com/payments/checkout/fulfillment?lang=python
Usage:
routes.py: Creation of Stripe Checkout Sessions (stripe.checkout.Session.create).
Webhook verification and event handling using Stripe’s official signature-checking pattern.
PaymentIntent confirmation workflow adapted from the Quickstart guide.
Handling asynchronous fulfilment of orders based on Checkout Session status.
Test cards and scenarios from Stripe Testing documentation used during development.
Notes: Stripe documentation guided the full implementation of secure payment flows, including Session creation, webhook signature validation, and post-payment order fulfilment. All Stripe-related functionality was written using the official API guidance, then adapted to the architecture of CharityConnect.


16. ReportLab PDF Generation Documentation used to undertsand the ChatGPT code (ReportLab, 2025)
URL: https://docs.reportlab.com/reportlab/userguide/ch2_graphics/
Usage:
build_receipt_pdf(): PDF canvas creation, drawing shapes, placing text, styling, and positioning elements.
Adding QR images using ImageReader and placing them on the PDF.
Managing page sizes (A4) and coordinate systems for clean layout.
Notes: The ReportLab User Guide informed the entire layout and PDF generation logic used to produce donation receipts, including header styling, text placement, and image embedding.


17. Python qrcode Library Documentation (Lincoln Loop, 2025)
URL: https://pypi.org/project/qrcode/
Usage:
Creation of QR images in memory for order verification.
Encoding the verification URL and exporting it to a BytesIO buffer.
Used directly inside the receipt generator prior to embedding via ReportLab.
Notes: The library was used to implement secure QR verification on receipts, following patterns from the official documentation.


18. Flask send_file Documentation (Pallets Projects, 2025)
URL: https://flask.palletsprojects.com/en/stable/api/#flask.send_file
Usage:
Returning PDF receipts as binary streams to the user.
Correct MIME-type configuration for PDF output.
Secure filename and streaming control.
Notes: Used for delivering dynamically-generated receipts to end users directly via the browser.


19. SQLAlchemy Case Expression Documentation (SQLAlchemy, 2025)
URL: https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.case
Usage:
Implementing custom sort order for organiser/charity verification lists.
Conditional SQL expressions inside list views for clearer admin displays.
Notes: This documentation guided more advanced list-ordering features required for the admin verification dashboard.

====================================================================================
# VERSION 2 END
====================================================================================

# VERSION 3 START
====================================================================================

20. OpenRouter API Documentation (OpenRouter, 2024)
URLs: 
https://openrouter.ai/docs
https://openrouter.ai/docs/api/reference/overview
https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request
Usage:
openrouter_client.py: Configuration of an OpenAI-compatible client using OpenRouter’s API endpoint.
routes.py: Sending structured system and user prompts to large language models for AI-assisted event description generation and advertising suggestions.
Notes: The OpenRouter documentation was referenced to understand request formatting, authentication using API keys, optional metadata headers, and response structures for chat completions. The API was used as an intermediary to access open-source large language models while maintaining compatibility with the OpenAI Python SDK. All prompt design and integration logic was written independently for the CharityConnect system.

21. OpenAI Python SDK Documentation (OpenAI, 2024)
URLs:
https://platform.openai.com/docs/api-reference/chat
https://platform.openai.com/docs/api-reference/chat/object
Usage:
openrouter_client.py: Use of the OpenAI client class and chat.completions.create() method to send messages and retrieve generated text.
Error handling logic adapted to support both attribute-based and dictionary-based SDK responses.
Notes: The OpenAI Python SDK documentation informed the structure of chat completion requests and response handling. Although the SDK is used, requests are routed through OpenRouter rather than OpenAI’s hosted models. The SDK was selected to reduce boilerplate and maintain a clean abstraction between application routes and AI provider logic.

22. Prompt Engineering Concepts (OpenAI, 2024)
URL: https://platform.openai.com/docs/guides/prompt-engineering
Usage:
routes.py: Construction of system and user prompts to constrain AI output, enforce tone (Irish/UK English), prevent fabricated claims, and require structured responses.
Notes: Prompt engineering guidance informed how instructions were framed for both event description generation and advertising suggestions. Prompts were designed to ensure factual, trustworthy, and reviewable output suitable for charity fundraising contexts. Final prompts were authored specifically for CharityConnect.

23. Flask-Login Documentation (Pallets Projects, 2026)
URLs:
https://flask-login.readthedocs.io/en/latest/
https://flask-login.readthedocs.io/en/latest/#login-example
Usage:
routes.py:
User authentication flows using login_user() and logout_user()
Session-based access control using @login_required
Redirecting users to their originally requested page via the next parameter
Managing logged-in user state during registration, login, and logout
Notes: The Flask-Login documentation informed the implementation of session-based authentication and access control within CharityConnect. Standard login and logout patterns were followed to manage user sessions securely, enforce protected routes, and maintain consistent authentication behaviour across organiser, admin, and user accounts. All authentication logic was implemented independently in accordance with Flask-Login’s official guidance.

24. Flask Request Object – JSON Parsing (Pallets Projects, 2024)
URL: https://flask.palletsprojects.com/en/stable/api/#flask.Request.get_json
Usage:
routes.py: Use of request.get_json(silent=True) to safely parse JSON payloads sent from the browser to AI-related Flask routes, avoiding exceptions when no JSON body is present.
Notes: This documentation was referenced to correctly handle JSON request bodies in Flask routes that receive asynchronous POST requests from client-side JavaScript. The silent=True option was used to ensure graceful failure and predictable request handling.

25. Flask Configuration System (Pallets Projects, 2024)
URL: https://flask.palletsprojects.com/en/stable/config/
Usage:
openrouter_client.py: Accessing configuration values via current_app.config to retrieve API keys, model identifiers, and site metadata.
config.py: Centralised configuration of environment variables for external services and application settings.
Notes: The Flask configuration documentation informed how environment-specific values are loaded and accessed safely within application code, supporting clean separation between configuration and logic.

=========================================================================================
# VERSION 3 END
=========================================================================================

# VERSION 4 START
=========================================================================================

26. SQLAlchemy ORM – Updating mapped objects and conditional state changes (SQLAlchemy, 2025)
URL: https://docs.sqlalchemy.org/en/20/orm/session_basics.html
Usage:
routes.py:
- Updating Order.status from PENDING to PAID only when a state change occurs.
- Updating Event.is_completed and Event.completed_at fields.
Notes: This documentation was referenced to ensure correct and consistent mutation of ORM-mapped objects, particularly where state transitions must only occur once (e.g. marking orders as paid). The guidance supports safe conditional updates followed by explicit session commits.

27. Flask-Mail Documentation – Sending transactional emails with attachments (Pallets Projects, 2025)
URL:https://flask-mail.readthedocs.io/en/latest/
Usage:
email_utils.py:
- Creating Message objects for transactional emails.
- Attaching dynamically-generated PDF receipts to outgoing emails.
- Sending email via a configured SMTP backend.
routes.py:
- Automatically emailing receipts after successful order finalisation.
- Preventing duplicate email sends using receipt_emailed_at tracking.

Notes: Flask-Mail documentation guided the implementation of receipt delivery via email, including attachment handling and SMTP integration. All email logic was written independently following official extension conventions.

28. Python csv Module Documentation (Python Software Foundation, 2025)
URL:https://docs.python.org/3/library/csv.html
Usage:
routes.py:
- Exporting audit log entries to CSV format for admin download.
- Writing header rows and serialising structured audit log data.
- Generating in-memory CSV files using StringIO.
Notes: The csv module was used to generate portable audit exports without introducing third-party dependencies, following patterns described in the Python standard library documentation.

29. Flask Response Object and Custom Headers (Pallets Projects, 2025)
URL: https://flask.palletsprojects.com/en/stable/api/#flask.Response
Usage:
routes.py:
- Returning CSV exports as downloadable files.
- Setting Content-Disposition headers to trigger browser downloads.
- Explicitly defining response MIME types.
Notes: Flask’s Response API was referenced to correctly construct non-HTML responses and deliver generated files securely to administrators.

30. Gmail SMTP Configuration and TLS Requirements (Google, 2024)
URLs: 
https://support.google.com/mail/answer/7126229
https://seatable.com/help/setup-gmail-smtp-email-seatable/
Usage:
.env configuration:
- SMTP host and port configuration (smtp.gmail.com, port 587).
- Enabling TLS for secure email transmission.
- Authentication using application-specific credentials.
Notes: Google’s official SMTP documentation informed the email delivery configuration used by CharityConnect. TLS enforcement and application passwords were used in line with recommended security practices for transactional email services.

=============================================================================================
# VERSION 4 END
=============================================================================================