from typing import Any
from app.repo.notification_repo import NotificationRepo
from app.utils.mail_service import MailService
from app.models.user import User
from app.db.db import db


class NotificationService:
    def __init__(self, notification_repo: NotificationRepo | None = None, mail_service: MailService | None = None):
        self.notification_repo = notification_repo or NotificationRepo()
        self.mail_service = mail_service or MailService()

    def notify_user(
        self,
        user_id: int,
        title: str,
        message: str,
        type: str | None = None,
        link_url: str | None = None,
        meta: dict[str, Any] | None = None,
        send_email: bool = False,
    ):
        notif = self.notification_repo.create(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            link_url=link_url,
            meta=meta,
        )

        if send_email:
            user = db.session.get(User, user_id)
            if user and user.email:
                subject = title
                text_body = message
                self.mail_service.send_mail(user.email, subject, text_body)

        return notif

    def notify_user_obj(
        self,
        user: User,
        title: str,
        message: str,
        type: str | None = None,
        link_url: str | None = None,
        meta: dict[str, Any] | None = None,
        send_email: bool = False,
    ):
        notif = self.notification_repo.create(
            user_id=user.id,
            title=title,
            message=message,
            type=type,
            link_url=link_url,
            meta=meta,
        )

        if send_email and user.email:
            self.mail_service.send_mail(user.email, title, message)

        return notif
