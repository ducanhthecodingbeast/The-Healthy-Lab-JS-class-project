from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user, require_role
from database import get_session
from models import Notification, User
from pagination import DEFAULT_LIMIT, DEFAULT_OFFSET, apply_pagination
from schemas import NotificationRead
from services.inventory import refresh_inventory_alerts


router = APIRouter()


@router.get("/notifications", response_model=list[NotificationRead])
def list_notifications(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    unread_only: bool = False,
    level: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = DEFAULT_OFFSET,
):
    require_role(current_user, ["admin", "staff", "chef"])
    refresh_inventory_alerts(session)
    session.commit()
    query = session.query(Notification)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    if level:
        query = query.filter(Notification.level == level)
    return apply_pagination(query.order_by(Notification.created_at.desc()), limit, offset).all()
