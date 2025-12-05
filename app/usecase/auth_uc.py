from datetime import datetime, timedelta, timezone

from app.repo.user_repo import UserRepo
from app.repo.permission_repo import PermissionRepo
from app.usecase.activitylog_uc import ActivityLogUC
from app.utils.mail_service import MailService
from app.utils.token_service import create_access_token
from app.utils.exception import BadRequest, PermissionDenied

from app.db.db import db


MAX_FAILED_ATTEMPTS = 5     
LOCK_MINUTES = 15           


class AuthUC:
    def __init__(
        self,
        user_repo: UserRepo | None = None,
        permission_repo: PermissionRepo | None = None,
        activitylog_uc: ActivityLogUC | None = None,
        mail_service: MailService | None = None,
    ):
        self.user_repo = user_repo or UserRepo()
        self.permission_repo = permission_repo or PermissionRepo()
        self.activitylog_uc = activitylog_uc or ActivityLogUC()
        self.mail_service = mail_service or MailService()

    def _get_user_by_identifier(self, identifier: str):
        user = self.user_repo.get_by_username(identifier)
        if not user:
            user = self.user_repo.get_by_email(identifier)
        return user

    def login(self, identifier: str, password: str):
        if not identifier or not password:
            raise BadRequest("Missing username/email or password")

        user = self._get_user_by_identifier(identifier)
        if not user:
            raise BadRequest("Invalid username/email or password")

        if user.is_deleted or not user.is_active:
            raise PermissionDenied("User is inactive or deleted")

        now = datetime.now(timezone.utc)

        if user.locked_until and user.locked_until > now:
            remaining = int((user.locked_until - now).total_seconds() // 60) + 1
            raise PermissionDenied(f"Account is locked. Try again in {remaining} minutes.")

        if not user.check_password(password):
            user.failed_attempts = (user.failed_attempts or 0) + 1

            if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = now + timedelta(minutes=LOCK_MINUTES)

                self.activitylog_uc.log_action(
                    user_id=user.id,
                    action="LOGIN_LOCKED",
                    details=f"User locked after {user.failed_attempts} failed login attempts"
                )

                if user.email:
                    subject = "[Mini ERP] Your account has been locked"
                    body = (
                        f"Hello {user.username},\n\n"
                        f"Your account has been locked for {LOCK_MINUTES} minutes "
                        f"after too many failed login attempts.\n"
                        "If this was not you, please contact your administrator."
                    )
                    self.mail_service.send_mail(user.email, subject, body)

            db.session.commit()
            raise BadRequest("Invalid username/email or password")

        user.failed_attempts = 0
        user.locked_until = None
        db.session.commit()

        self.activitylog_uc.log_action(
            user_id=user.id,
            action="LOGIN_SUCCESS",
            details="User logged in successfully"
        )

        token = create_access_token(
            user_id=user.id,
            username=user.username,
            permissions=user.permission_codes
        )
    
        role_code = user.role.code if user.role else None
    
        intern_id = None
        if hasattr(user, 'intern') and user.intern:
            intern_id = user.intern.id
        else:
            from app.models.intern import Intern
            intern = Intern.query.filter_by(user_id=user.id).first()
            if intern:
                intern_id = intern.id

        return {
            "token": token,  
            "user": user.to_dict(),
            "permissions": user.permission_codes,
            "role_code": role_code,  
            "intern_id": intern_id   
        }
    def change_password(self, user_id, old_password, new_password):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if not user.check_password(old_password):
            raise ValueError("Old password is incorrect")

        user.set_password(new_password)

        db.session.add(user)
        db.session.commit()

        self.activitylog_uc.log_action(
            user_id=user_id,
            action="CHANGE_PASSWORD",
            details="User changed password"
        )

        return {"message": "Password updated successfully"}
