from app.repo.permission_repo import PermissionRepo
from app.usecase.activitylog_uc import ActivityLogUC


class PermissionUC:
    def __init__(
        self,
        permission_repo=None,
        activitylog_uc=None
    ):
        self.permission_repo = permission_repo or PermissionRepo()
        self.activitylog_uc = activitylog_uc or ActivityLogUC()

    def create_permission(self, user_id, data):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")
        perm = self.permission_repo.create(data)
        self.activitylog_uc.log_action(
            user_id=user_id,
            action="CREATE_PERMISSION",
            details=f"Create permission {perm.code}"
        )
        return perm.to_dict()

    def get_all_permissions(self, user_id):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")
        perms = self.permission_repo.get_all()
        return [p.to_dict() for p in perms]

    def get_permission(self, user_id, permission_id):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")
        p = self.permission_repo.get_by_id(permission_id)
        return p.to_dict() if p else None

    def update_permission(self, user_id, permission_id, data):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")
        updated = self.permission_repo.update(permission_id, data)
        if updated:
            self.activitylog_uc.log_action(
                user_id=user_id,
                action="UPDATE_PERMISSION",
                details=f"Update permission {updated.code}"
            )
            return updated.to_dict()
        return None

    def delete_permission(self, user_id, permission_id):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")
        ok = self.permission_repo.delete(permission_id)
        if ok:
            self.activitylog_uc.log_action(
                user_id=user_id,
                action="DELETE_PERMISSION",
                details=f"Delete permission ID {permission_id}"
            )
        return ok

    def search_permissions(self, user_id, keyword):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")
        perms = self.permission_repo.search(keyword)
        return [p.to_dict() for p in perms]

    def get_permission_by_code(self, user_id, code):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")
        p = self.permission_repo.get_by_code(code)
        return p.to_dict() if p else None
