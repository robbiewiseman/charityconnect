# VERSION 4 START
from models import db, AuditLog
from flask_login import current_user

def log_action(action, entity_type, entity_id=None, meta=None):
    # Records an action in the audit log for traceability.

    # Create a new audit log entry
    log = AuditLog(
        # ID of the user performing the action (if logged in)
        actor_id=getattr(current_user, "id", None),
        # Role of the user at the time of the action
        actor_role=getattr(current_user, "role", None),
        # Action name (e.g. ORDER_PAID, RECEIPT_EMAILED)
        action=action,
        # Type of entity affected (e.g. Order, Event, Organiser)
        entity_type=entity_type,
        # ID of the affected entity
        entity_id=entity_id,
        # Extra contextual data stored as JSON
        meta=meta,
    )
    # Add the audit entry to the database session
    db.session.add(log)
# VERSION 4 END