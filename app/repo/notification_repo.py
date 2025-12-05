from app.models.notification import Notification
from app.db.db import db
from datetime import datetime


class NotificationRepo:
    def create(self, data: dict):
        notification = Notification(
            user_id=data["user_id"],
            title=data["title"],
            message=data["message"],
            type=data.get("type"),
            link_url=data.get("link_url"),
            meta=data.get("meta"),
            is_read=data.get("is_read", False),
            created_at=datetime.utcnow()
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    def list_for_user(self, user_id: int, only_unread: bool = False):
        query = Notification.query.filter_by(user_id=user_id)
        
        if only_unread:
            query = query.filter_by(is_read=False)
        
        return query.order_by(Notification.created_at.desc()).all()

    def get_by_id(self, notif_id: int):
        return Notification.query.get(notif_id)

    def mark_read(self, notif_id: int, user_id: int = None) -> bool:
        notification = self.get_by_id(notif_id)
        
        if not notification:
            return False
        
        if user_id and notification.user_id != user_id:
            return False
        
        notification.is_read = True
        db.session.commit()
        return True

    def mark_all_read(self, user_id: int) -> int:
        count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({"is_read": True})
        
        db.session.commit()
        return count

    def delete(self, notif_id: int, user_id: int = None) -> bool:
        notification = self.get_by_id(notif_id)
        
        if not notification:
            return False
        
        if user_id and notification.user_id != user_id:
            return False
        
        db.session.delete(notification)
        db.session.commit()
        return True

    def delete_old_notifications(self, days: int = 30):
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        count = Notification.query.filter(
            Notification.created_at < cutoff,
            Notification.is_read == True
        ).delete()
        
        db.session.commit()
        return count