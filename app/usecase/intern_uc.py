import re
from datetime import datetime, date
from app.repo.intern_repo import InternRepo
from app.repo.intern_project_repo import InternProjectRepo
from app.repo.permission_repo import PermissionRepo
from app.usecase.activitylog_uc import ActivityLogUC
from app.utils.exception import NotFound, BadRequest

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

class InternUC:
    def __init__(
        self,
        intern_repo=None,
        intern_project_repo=None,
        permission_repo=None,
        activitylog_uc=None
    ):
        self.intern_repo = intern_repo or InternRepo()
        self.intern_project_repo = intern_project_repo or InternProjectRepo()
        self.permission_repo = permission_repo or PermissionRepo()
        self.activitylog_uc = activitylog_uc or ActivityLogUC()

    def _parse_date(self, value, field_name):
        if value is None or value == "":
            return None
        if isinstance(value, date):
            return value
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            raise BadRequest(f"Invalid date format for {field_name}, expected YYYY-MM-DD")

    def _normalize_and_validate(self, data, is_update=False, current_intern=None):
        name = data.get("name") if "name" in data or not is_update else current_intern.name
        email = data.get("email") if "email" in data or not is_update else current_intern.email
        university = data.get("university") if "university" in data else (current_intern.university if is_update and current_intern else None)
        major = data.get("major") if "major" in data else (current_intern.major if is_update and current_intern else None)
        start_date_raw = data.get("start_date") if "start_date" in data else (current_intern.start_date if is_update and current_intern else None)
        end_date_raw = data.get("end_date") if "end_date" in data else (current_intern.end_date if is_update and current_intern else None)

        name = (name or "").strip()
        email = (email or "").strip().lower()
        university = (university or "").strip() or None
        major = (major or "").strip() or None

        if not name:
            raise BadRequest("Name is required")
        if not email:
            raise BadRequest("Email is required")

        if len(name) > 100:
            raise BadRequest("Name is too long (max 100 characters)")
        if len(email) > 120:
            raise BadRequest("Email is too long (max 120 characters)")
        if university and len(university) > 120:
            raise BadRequest("University is too long (max 120 characters)")
        if major and len(major) > 100:
            raise BadRequest("Major is too long (max 100 characters)")

        if not EMAIL_RE.match(email):
            raise BadRequest("Invalid email format")

        if major:
            allowed_majors = {"IT", "Business", "Design", "Marketing"}
            if major not in allowed_majors:
                raise BadRequest(f"Major must be one of: {', '.join(sorted(allowed_majors))}")

        start_date = self._parse_date(start_date_raw, "start_date") or date.today()
        end_date = self._parse_date(end_date_raw, "end_date")

        if end_date and end_date < start_date:
            raise BadRequest("End date cannot be earlier than start date")

        if not is_update:
            existing = self.intern_repo.get_any_by_email(email)
            if existing and not existing.is_deleted:
                raise BadRequest("An intern with this email already exists")
        else:
            if email != current_intern.email:
                if current_intern.feedbacks or current_intern.intern_projects or current_intern.training_plans:
                    raise BadRequest("Cannot change email because intern already has related records")
                existing = self.intern_repo.get_any_by_email(email)
                if existing and existing.id != current_intern.id and not existing.is_deleted:
                    raise BadRequest("An intern with this email already exists")

        clean_data = {
            "name": name,
            "email": email,
            "university": university,
            "major": major,
            "start_date": start_date,
            "end_date": end_date,
        }

        return clean_data

    def get_all_interns(self, user_id):
        self.permission_repo.ensure(user_id, "INTERN_VIEW")
        interns = self.intern_repo.get_all()
        return [i.to_dict(with_counts=True) for i in interns]

    def get_intern_by_id(self, user_id, intern_id):
        self.permission_repo.ensure(user_id, "INTERN_VIEW")
        intern = self.intern_repo.get_by_id(intern_id)
        if not intern:
            raise NotFound("Intern not found")
        return intern.to_dict(with_counts=True)

    def get_intern_by_email(self, user_id, email):
        self.permission_repo.ensure(user_id, "INTERN_VIEW")
        email = (email or "").strip().lower()
        if not email:
            raise BadRequest("Email is required")
        intern = self.intern_repo.get_by_email(email)
        if not intern:
            raise NotFound("Intern not found")
        return intern.to_dict(with_counts=True)

    def create_intern(self, user_id, data):
        self.permission_repo.ensure(user_id, "INTERN_CREATE")
        clean_data = self._normalize_and_validate(data or {}, is_update=False)
        intern = self.intern_repo.create(clean_data)
        self.activitylog_uc.log_action(
            user_id=user_id,
            action="CREATE_INTERN",
            details=f"Created intern {intern.name}"
        )
        return intern.to_dict()

    def update_intern(self, user_id, intern_id, data):
        self.permission_repo.ensure(user_id, "INTERN_UPDATE")
        if not data:
            raise BadRequest("No data to update")

        current = self.intern_repo.get_by_id(intern_id)
        if not current:
            raise NotFound("Intern not found")

        clean_data = self._normalize_and_validate(data, is_update=True, current_intern=current)
        updated = self.intern_repo.update(intern_id, clean_data)
        if not updated:
            raise NotFound("Intern not found")

        self.activitylog_uc.log_action(
            user_id=user_id,
            action="UPDATE_INTERN",
            details=f"Updated intern {updated.name}"
        )

        return updated.to_dict()

    def delete_intern(self, user_id, intern_id, soft=True):
        self.permission_repo.ensure(user_id, "INTERN_DELETE")
        ok = self.intern_repo.delete(intern_id, soft=soft)
        if not ok:
            raise NotFound("Intern not found")
        action = "SOFT_DELETE_INTERN" if soft else "HARD_DELETE_INTERN"
        self.activitylog_uc.log_action(
            user_id=user_id,
            action=action,
            details=f"{action} ID {intern_id}"
        )
        return True

    def get_projects_of_intern(self, user_id, intern_id):
        self.permission_repo.ensure(user_id, "PROJECT_VIEW")
        intern = self.intern_repo.get_by_id(intern_id)
        if not intern:
            raise NotFound("Intern not found")
        return self.intern_project_repo.get_projects_of_intern(intern_id)

    def close_internship(self, user_id, intern_id):
        self.permission_repo.ensure(user_id, "INTERN_UPDATE")

        intern = self.intern_repo.get_by_id(intern_id)
        if not intern:
            raise NotFound("Intern not found")

        if intern.end_date:
            raise BadRequest("Internship already closed")

        clean_data = {
            "end_date": date.today()
        }

        updated = self.intern_repo.update(intern_id, clean_data)

        self.activitylog_uc.log_action(
            user_id=user_id,
            action="CLOSE_INTERNSHIP",
            details=f"Closed internship for {updated.name}"
        )

        return {"success": True, "end_date": updated.end_date.isoformat()}
