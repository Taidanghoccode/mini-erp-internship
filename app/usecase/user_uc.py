import re

from app.repo.user_repo import UserRepo
from app.repo.role_repo import RoleRepo
from app.repo.permission_repo import PermissionRepo
from app.usecase.activitylog_uc import ActivityLogUC
from app.utils.mail_service import MailService
from app.utils.notification_service import NotificationService
from app.utils.exception import NotFound, BadRequest


def validate_strong_password(pw: str):
    if not pw:
        raise BadRequest("Password is required")

    if len(pw) < 8:
        raise BadRequest("Password must be at least 8 characters")

    if not re.search(r"[A-Z]", pw):
        raise BadRequest("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", pw):
        raise BadRequest("Password must contain at least one lowercase letter")

    if not re.search(r"[0-9]", pw):
        raise BadRequest("Password must contain at least one number")

    if not re.search(r"[\W_]", pw):
        raise BadRequest("Password must contain at least one special character")


class UserUC:
    def __init__(
        self,
        user_repo: UserRepo | None = None,
        role_repo: RoleRepo | None = None,
        permission_repo: PermissionRepo | None = None,
        activitylog_uc: ActivityLogUC | None = None,
        mail_service: MailService | None = None,
        notification_service: NotificationService | None = None,
    ):
        self.user_repo = user_repo or UserRepo()
        self.role_repo = role_repo or RoleRepo()
        self.permission_repo = permission_repo or PermissionRepo()
        self.activitylog_uc = activitylog_uc or ActivityLogUC()
        self.mail_service = mail_service or MailService()
        self.notification_service = notification_service or NotificationService()

    def _require(self, user_id: int, perm_code: str):
        self.permission_repo.ensure(user_id, perm_code)

    def create_user(self, user_id: int, data: dict):
        self._require(user_id, "USER_MANAGE")

        if not data.get("username") or not data.get("email") or not data.get("password"):
            raise BadRequest("Missing username, email or password")

        validate_strong_password(data["password"])

        role_id = data.get("role_id")
        if role_id:
            role = self.role_repo.get_by_id(role_id)
            if not role:
                raise NotFound("Role not found")

        user = self.user_repo.create(data)

        self.activitylog_uc.log_action(
            user_id=user_id,
            action="CREATE_USER",
            details=f"Create user {user.username}"
        )

        if user.email:
            subject = "Your Mini ERP account"
            text_body = (
                f"Hello {user.username},\n\n"
                f"Your account has been created.\n"
                f"Username: {user.username}\n"
                f"Email: {user.email}\n"
                f"Password: {data['password']}\n"
                f"Role ID: {user.role_id or '-'}\n\n"
                f"Please login and change your password."
            )
            self.mail_service.send_mail(user.email, subject, text_body)

        self.notification_service.notify_user(
            user_id=user.id,
            title="Your account is ready",
            message="Your account has been created. You can now login to the system.",
            type="system",
        )

        return user.to_dict()

    def get_all_users(self, user_id: int):
        self._require(user_id, "USER_MANAGE")
        users = self.user_repo.get_all()
        return [u.to_dict() for u in users]

    def get_user_by_id(self, user_id: int, target_id: int):
        self._require(user_id, "USER_MANAGE")
        user = self.user_repo.get_by_id(target_id)
        if not user:
            raise NotFound("User not found")
        return user.to_dict()

    def update_user(self, user_id: int, target_id: int, data: dict):
        self._require(user_id, "USER_MANAGE")

        if "password" in data and data["password"]:
            validate_strong_password(data["password"])

        updated = self.user_repo.update(target_id, data)
        if not updated:
            raise NotFound("User not found")

        self.activitylog_uc.log_action(
            user_id=user_id,
            action="UPDATE_USER",
            details=f"Update user {updated.username}"
        )

        if "password" in data and updated.email:
            subject = "Your password has been updated"
            text_body = (
                f"Hello {updated.username},\n\n"
                "Your account password has been updated by administrator.\n"
                "If this was not you, please contact support."
            )
            self.mail_service.send_mail(updated.email, subject, text_body)

        return updated.to_dict()

    def delete_user(self, user_id: int, target_id: int, soft: bool = True):
        self._require(user_id, "USER_MANAGE")
        ok = self.user_repo.delete(target_id, soft=soft)
        if not ok:
            raise NotFound("User not found")

        action = "SOFT_DELETE_USER" if soft else "HARD_DELETE_USER"
        self.activitylog_uc.log_action(
            user_id=user_id,
            action=action,
            details=f"{action} ID {target_id}"
        )

        return True

    def assign_role(self, user_id: int, target_id: int, role_id: int):
        self._require(user_id, "ROLE_MANAGE")

        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFound("Role not found")

        updated = self.user_repo.assign_role(target_id, role_id)
        if not updated:
            raise NotFound("User not found")

        self.activitylog_uc.log_action(
            user_id=user_id,
            action="ASSIGN_ROLE",
            details=f"Assign role {role.code} to user ID {target_id}"
        )

        self.notification_service.notify_user(
            user_id=updated.id,
            title="Your role has changed",
            message=f"Your role has been updated to {role.name}.",
            type="system",
        )

        return updated.to_dict()

    def get_users_by_role(self, user_id: int, role_code: str):
        self._require(user_id, "USER_MANAGE")
        users = self.user_repo.get_by_role(role_code)
        return [u.to_dict() for u in users]

    def get_profile(self, user_id: int):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFound("User not found")

        perms = user.permission_codes

        if user.role and user.role.code != "ADMIN":
            return {
                "user": user.to_dict(),
                "permissions": perms,
                "activity_logs": []
            }

        raw_logs = self.activitylog_uc.get_logs_by_user(user_id)

        activity_logs = []
        for l in raw_logs:
            ts = l.get("timestamp")
            if hasattr(ts, "strftime"):
                ts = ts.strftime("%Y-%m-%d %H:%M:%S")

            activity_logs.append({
                "action": l.get("action"),
                "details": l.get("details"),
                "timestamp": ts
            })

        return {
            "user": user.to_dict(),
            "permissions": perms,
            "activity_logs": activity_logs
        }
