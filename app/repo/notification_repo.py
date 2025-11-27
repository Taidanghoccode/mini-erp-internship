from typing import List, Optional
from app.db.db import db
from app.models.notification import Notification


class NotificationRepo:
    def create(
        self,
        user_id: int,
        title: str,
        message: str,
        type: str | None = None,
        link_url: str | None = None,
        meta: dict | None = None,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            link_url=link_url,
            meta=meta,
        )
        db.session.add(notif)
        db.session.commit()
        return notif

    def get_by_id(self, notif_id: int) -> Optional[Notification]:
        return Notification.query.get(notif_id)

    def list_for_user(self, user_id: int, only_unread: bool = False) -> List[Notification]:
        q = Notification.query.filter_by(user_id=user_id)
        if only_unread:
            q = q.filter_by(is_read=False)
        return q.order_by(Notification.created_at.desc()).all()

    def mark_read(self, notif_id: int, user_id: int | None = None) -> bool:
        q = Notification.query.filter_by(id=notif_id)
        if user_id is not None:
            q = q.filter_by(user_id=user_id)
        notif = q.first()
        if not notif:
            return False
        if not notif.is_read:
            notif.is_read = True
            db.session.commit()
        return True

    def mark_all_read(self, user_id: int) -> int:
        q = Notification.query.filter_by(user_id=user_id, is_read=False)
        count = q.count()
        if count:
            q.update({"is_read": True})
            db.session.commit()
        return count
