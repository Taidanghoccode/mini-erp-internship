from datetime import date
from app.repo.project_repo import ProjectRepo
from app.repo.intern_project_repo import InternProjectRepo
from app.repo.permission_repo import PermissionRepo
from app.usecase.activitylog_uc import ActivityLogUC
from app.models.user import User


def _has_perm(user_id, code):
    user = User.query.get(user_id)
    if not user:
        raise PermissionError("User not found")
    if code not in user.permission_codes:
        raise PermissionError(f"No permission: {code}")
    return user


class ProjectUC:
    def __init__(
        self,
        project_repo=None,
        intern_project_repo=None,
        permission_repo=None,
        activitylog_uc=None,
    ):
        self.project_repo = project_repo or ProjectRepo()
        self.intern_project_repo = intern_project_repo or InternProjectRepo()
        self.permission_repo = permission_repo or PermissionRepo()
        self.activitylog_uc = activitylog_uc or ActivityLogUC()

    def get_all_projects(self, user_id):
        user = _has_perm(user_id, "PROJECT_VIEW")

        if user.role.code in ["ADMIN", "MENTOR"]:
            projects = self.project_repo.get_all()
            return [p.to_dict(with_counts=True) for p in projects]

        if user.role.code == "INTERN":
            intern = user.intern_profile
            assigned = self.intern_project_repo.get_projects_by_intern(intern.id)

            return assigned


    def get_project_by_id(self, user_id, project_id):
        user = _has_perm(user_id, "PROJECT_VIEW")  # kiểm tra user tồn tại + perm

        project = self.project_repo.get_by_id(project_id)
        if not project:
            return None

        if user.role.code == "INTERN":
            intern = user.intern_profile
            if not intern:
                raise PermissionError("Invalid intern profile")

            assigned = self.intern_project_repo.get_by_intern_and_project(intern.id, project_id)
            if not assigned:
                raise PermissionError("You cannot view this project because you are not assigned to it")

        return project.to_dict(with_counts=True)

    
    def create_project(self, user_id, data):
        _has_perm(user_id, "PROJECT_CREATE")

        project = self.project_repo.create(data)

        self.activitylog_uc.log_action(
            user_id=user_id,
            action="CREATE_PROJECT",
            details=f"Create project {project.title}",
        )

        return project.to_dict()

    def update_project(self, user_id, project_id, data):
        _has_perm(user_id, "PROJECT_UPDATE")

        project = self.project_repo.get_by_id(project_id)
        if not project:
            return None

        old_status = project.status
        new_status = data.get("status", old_status)

        if old_status == "done" and new_status != "done":
            raise ValueError("Cannot change status of a completed project")

        if new_status == "done" and old_status != "done":
            data["end_date"] = date.today().isoformat()

        updated = self.project_repo.update(project_id, data)

        if updated:
            self.activitylog_uc.log_action(
                user_id=user_id,
                action="UPDATE_PROJECT",
                details=f"Update project {updated.title}: status={new_status}",
            )
            return updated.to_dict()

        return None

    def delete_project(self, user_id, project_id, soft=True):
        _has_perm(user_id, "PROJECT_DELETE")

        ok = self.project_repo.delete(project_id, soft=soft)

        if ok:
            action = "SOFT_DELETE_PROJECT" if soft else "HARD_DELETE_PROJECT"
            self.activitylog_uc.log_action(
                user_id=user_id,
                action=action,
                details=f"{action} ID {project_id}",
            )

        return ok

    def get_interns_of_project(self, user_id, project_id):
        _has_perm(user_id, "PROJECT_VIEW")
        return self.intern_project_repo.get_interns_of_project(project_id)

    def assign_intern(self, user_id, intern_id, project_id, role):
        _has_perm(user_id, "PROJECT_ASSIGN_INTERN")

        link = self.intern_project_repo.create_link(intern_id, project_id, role)

        self.activitylog_uc.log_action(
            user_id=user_id,
            action="ASSIGN_INTERN",
            details=f"Assign intern {intern_id} to project {project_id}",
        )

        return link.to_dict()

    def remove_intern(self, user_id, intern_id, project_id):
        _has_perm(user_id, "PROJECT_ASSIGN_INTERN")

        ok = self.intern_project_repo.remove_link(intern_id, project_id)

        if ok:
            self.activitylog_uc.log_action(
                user_id=user_id,
                action="REMOVE_INTERN",
                details=f"Remove intern {intern_id} from project {project_id}",
            )

        return ok