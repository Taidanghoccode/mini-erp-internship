import re
from datetime import datetime, date

from app.repo.intern_repo import InternRepo
from app.repo.user_repo import UserRepo
from app.repo.permission_repo import PermissionRepo
from app.usecase.activitylog_uc import ActivityLogUC
from app.utils.exception import NotFound, BadRequest
from app.utils.mail_service import MailService

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class InternUC:

    def __init__(
        self,
        intern_repo=None,
        user_repo=None,
        permission_repo=None,
        activitylog_uc=None,
        mail_service=None
    ):
        self.intern_repo = intern_repo or InternRepo()
        self.user_repo = user_repo or UserRepo()
        self.permission_repo = permission_repo or PermissionRepo()
        self.activitylog_uc = activitylog_uc or ActivityLogUC()
        self.mail_service = mail_service or MailService()

    def _validate_email(self, email):
        if not EMAIL_RE.match(email):
            raise BadRequest("Invalid email format")

    def create_intern(self, user_id, data):
        self.permission_repo.ensure(user_id, "INTERN_CREATE")

        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        university = data.get("university")
        major = data.get("major")

        user_link_id = data.get("user_id") or None

        if not name:
            raise BadRequest("Name is required")
        if not email:
            raise BadRequest("Email is required")

        self._validate_email(email)

        if self.intern_repo.get_any_by_email(email):
            raise BadRequest("This email is already used")

        if user_link_id:
            user = self.user_repo.get_by_id(user_link_id)
            if not user:
                raise BadRequest("Linked user does not exist")

            existed = self.intern_repo.get_by_user_id(user_link_id)
            if existed:
                raise BadRequest("This user is already linked to another intern")

        intern = self.intern_repo.create({
            "name": name,
            "email": email,
            "university": university,
            "major": major,
            "user_id": user_link_id
        })

        self.activitylog_uc.log_action(
            user_id=user_id,
            action="CREATE_INTERN",
            details=f"Created intern {intern.name}"
        )

        if user_link_id:
            user = self.user_repo.get_by_id(user_link_id)
            self.mail_service.send_mail(
                user.email,
                "Your Internship Account",
                f"Hello {intern.name},\n\n"
                "Your Mini ERP account is ready.\n\n"
                f"Username: {user.username}\n"
                f"Email: {user.email}\n\n"
                "Please login and update your password.\n"
                )
            

        return intern.to_dict(with_counts=True)

    def update_intern(self, user_id, intern_id, data):
        self.permission_repo.ensure(user_id, "INTERN_UPDATE")

        intern = self.intern_repo.get_by_id(intern_id)
        if not intern:
            raise NotFound("Intern not found")

        if "email" in data:
            new_email = (data["email"] or "").strip().lower()

            if new_email != intern.email:
                self._validate_email(new_email)

                exists = self.intern_repo.get_any_by_email(new_email)
                if exists and exists.id != intern.id:
                    raise BadRequest("This email is already used")

                intern.email = new_email

        if "user_id" in data:
            new_uid = data.get("user_id") or None

            if new_uid != intern.user_id:

                if new_uid:
                    user = self.user_repo.get_by_id(new_uid)
                    if not user:
                        raise BadRequest("Linked user does not exist")

                    exists = self.intern_repo.get_by_user_id(new_uid)
                    if exists and exists.id != intern.id:
                        raise BadRequest("This user is already linked to another intern")

                intern.user_id = new_uid

        if "name" in data:
            intern.name = data["name"].strip()
        if "university" in data:
            intern.university = data["university"]
        if "major" in data:
            intern.major = data["major"]

        updated = self.intern_repo.update(intern)

        self.activitylog_uc.log_action(
            user_id=user_id,
            action="UPDATE_INTERN",
            details=f"Updated intern {intern.name}"
        )

        return updated.to_dict(with_counts=True)


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

    def delete_intern(self, user_id, intern_id, soft=True):
        self.permission_repo.ensure(user_id, "INTERN_DELETE")
        return self.intern_repo.delete(intern_id, soft=soft)

    def get_projects_of_intern(self, user_id, intern_id):
        self.permission_repo.ensure(user_id, "PROJECT_VIEW")

        intern = self.intern_repo.get_by_id(intern_id)
        if not intern:
            raise NotFound("Intern not found")

        projects = self.intern_repo.get_projects(intern_id)
        return [p.to_dict(with_counts=True) for p in projects]


    def close_internship(self, user_id, intern_id):
        self.permission_repo.ensure(user_id, "INTERN_UPDATE")

        intern = self.intern_repo.get_by_id(intern_id)
        if not intern:
            raise NotFound("Intern not found")

        intern.end_date = date.today()
        updated = self.intern_repo.update(intern)

        self.activitylog_uc.log_action(
            user_id=user_id,
            action="CLOSE_INTERNSHIP",
            details=f"Closed internship of {intern.name}"
        )

        return updated.to_dict(with_counts=True)
