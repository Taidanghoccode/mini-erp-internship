from app.repo.role_repo import RoleRepo
from app.repo.permission_repo import PermissionRepo
from app.usecase.activitylog_uc import ActivityLogUC


class RoleUC:
    def __init__(
        self,
        role_repo=None,
        permission_repo=None,
        activitylog_uc=None
    ):
        self.role_repo = role_repo or RoleRepo()
        self.permission_repo = permission_repo or PermissionRepo()
        self.activitylog_uc = activitylog_uc or ActivityLogUC()

    def create_role(self, user_id, data):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")
        role = self.role_repo.create(data)
        self.activitylog_uc.log_action(
            user_id=user_id,
            action="CREATE_ROLE",
            details=f"Create role {role.name}"
        )
        return role.to_dict()

    def get_all_roles(self, user_id):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")
        roles = self.role_repo.get_all()
        return [r.to_dict() for r in roles]

    def get_role(self, user_id, role_id):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")
        role = self.role_repo.get_by_id(role_id)
        return role.to_dict() if role else None

    def update_role(self, user_id, role_id, data):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")
        updated = self.role_repo.update(role_id, data)
        if updated:
            self.activitylog_uc.log_action(
                user_id=user_id,
                action="UPDATE_ROLE",
                details=f"Update role {updated.name}"
            )
            return updated.to_dict()
        return None

    def delete_role(self, user_id, role_id):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")
        ok = self.role_repo.delete(role_id)
        if ok:
            self.activitylog_uc.log_action(
                user_id=user_id,
                action="DELETE_ROLE",
                details=f"Delete role ID {role_id}"
            )
        return ok

    def assign_permission(self, user_id, role_id, permission_id):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")
        result = self.role_repo.assign_permission(role_id, permission_id)
        self.activitylog_uc.log_action(
            user_id=user_id,
            action="ASSIGN_PERMISSION",
            details=f"Assign permission {permission_id} to role {role_id}"
        )
        return result.to_dict()

    def remove_permission(self, user_id, role_id, permission_id):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")
        result = self.role_repo.remove_permission(role_id, permission_id)
        self.activitylog_uc.log_action(
            user_id=user_id,
            action="REMOVE_PERMISSION",
            details=f"Remove permission {permission_id} from role {role_id}"
        )
        return result.to_dict()

    def get_role_by_id(self, user_id, role_id):
        if not self.permission_repo.user_has(user_id, "ROLE_MANAGE"):
            raise PermissionError("No permission: ROLE_MANAGE")

        role = self.role_repo.get_by_id(role_id)
        return role.to_dict() if role else None
