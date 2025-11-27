from app.repo.user_repo import UserRepo
from app.repo.permission_repo import PermissionRepo
from app.utils.token_service import create_access_token
from app.usecase.activitylog_uc import ActivityLogUC
from app.utils.mail_service import MailService

class AuthUC:
    def __init__(self, user_repo=None, permission_repo=None, activitylog_uc=None, mail_service=None):
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
        user = self._get_user_by_identifier(identifier)
        if not user:
            raise ValueError("Invalid username/email or password")

        if user.is_deleted or not user.is_active:
            raise PermissionError("User is inactive or deleted")

        if not user.check_password(password):
            raise ValueError("Invalid username/email or password")

        permissions = user.permission_codes or []

        token = create_access_token(
            user_id=user.id,
            username=user.username,
            permissions=permissions,
        )
        return {
            "token": token,
            "user": user.to_dict(),
            "permissions": permissions
        }

    def logout(self, token: str):
        return {"message": "Logged out"}
    
    def change_password(self, user_id: int, old_password: str, new_password: str):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.is_deleted or not user.is_active:
            raise PermissionError("User is inactive or deleted")
        
        if not user.check_password(old_password):
            raise ValueError("Current password is incorrect")
        
        if len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters")
        
        if old_password == new_password:
            raise ValueError("New password must be different from current password")
        
        updated = self.user_repo.update(user_id, {"password": new_password})
        
        self.activitylog_uc.log_action(
            user_id=user_id,
            action="CHANGE_PASSWORD",
            details="Password changed successfully"
        )
        
        if user.email:
            subject = "Password Changed Successfully"
            text_body = (
                f"Hello {user.username},\n\n"
                "Your password has been changed successfully.\n"
                "If you did not make this change, please contact support immediately.\n\n"
                "Best regards,\n"
                "Mini ERP Team"
            )
            self.mail_service.send_mail(user.email, subject, text_body)
        
        return {"message": "Password changed successfully"}