from app.repo.notification_repo import NotificationRepo


class NotificationUC:
    def __init__(self, notification_repo: NotificationRepo | None = None):
        self.notification_repo = notification_repo or NotificationRepo()

    def list_for_user(self, user_id: int, only_unread: bool = False):
        items = self.notification_repo.list_for_user(user_id, only_unread=only_unread)
        return [n.to_dict() for n in items]

    def mark_read(self, user_id: int, notif_id: int) -> bool:
        return self.notification_repo.mark_read(notif_id, user_id=user_id)

    def mark_all_read(self, user_id: int) -> int:
        return self.notification_repo.mark_all_read(user_id)
