from sqlalchemy.orm import Session

from models import Membership, Notification, Order, OrderMembershipAward, Payment, User
from services.notifications import create_notification_once


def membership_tier(points: int) -> str:
    if points >= 250:
        return "gold"
    if points >= 100:
        return "silver"
    return "bronze"


def get_or_create_membership(user: User, session: Session) -> Membership:
    membership = session.query(Membership).filter(Membership.user_id == user.id).first()
    if membership:
        return membership

    membership = Membership(user_id=user.id, points=0, tier="bronze")
    session.add(membership)
    session.flush()
    return membership


def award_order_membership_points(order: Order, session: Session) -> Membership | None:
    if order.status != "delivered":
        return None
    paid_payment = session.query(Payment).filter(Payment.order_id == order.id, Payment.status == "paid").first()
    if not paid_payment:
        return None
    existing_award = session.query(OrderMembershipAward).filter(OrderMembershipAward.order_id == order.id).first()
    if existing_award:
        return None

    customer = session.get(User, order.customer_id)
    if not customer:
        return None

    membership = get_or_create_membership(customer, session)
    previous_tier = membership.tier
    points = int(order.total_price)
    membership.points += points
    membership.tier = membership_tier(membership.points)
    session.add(membership)
    session.add(OrderMembershipAward(order_id=order.id, points_awarded=points))
    if membership.tier != previous_tier:
        create_membership_upgrade_notification(session, order.customer_id, membership.tier)
    return membership


def create_membership_upgrade_notification(session: Session, user_id: int, tier: str) -> None:
    title = "Membership tier upgrade"
    message = f"User #{user_id} reached {tier} tier."
    existing = session.query(Notification).filter(Notification.title == title, Notification.message == message).first()
    if not existing:
        create_notification_once(session, title, message, "info")
