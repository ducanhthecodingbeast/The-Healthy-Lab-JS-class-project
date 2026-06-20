from sqlalchemy.orm import Session

from models import Notification


def create_notification_once(session: Session, title: str, message: str, level: str = "info"):
    existing = (
        session.query(Notification)
        .filter(Notification.title == title, Notification.message == message, Notification.is_read.is_(False))
        .first()
    )
    if existing:
        return existing

    notification = Notification(title=title, message=message, level=level)
    session.add(notification)
    return notification
