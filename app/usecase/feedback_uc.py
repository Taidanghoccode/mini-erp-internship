from datetime import datetime
from app.repo.feedback_repo import FeedbackRepo
from app.repo.notification_repo import NotificationRepo
from app.repo.intern_repo import InternRepo
from app.repo.project_repo import ProjectRepo
from app.repo.user_repo import UserRepo
from app.repo.permission_repo import PermissionRepo
from app.utils.mail_service import MailService
from app.models.feedback import FeedbackType
from app.utils.notification_service import NotificationService


class FeedbackUC:
    def __init__(
        self,
        feedback_repo=None,
        notification_repo=None,
        intern_repo=None,
        project_repo=None,
        user_repo=None,
        mail_service=None,
        permission_repo=None
    ):
        self.feedback_repo = feedback_repo or FeedbackRepo()
        self.notification_repo = notification_repo or NotificationRepo()
        self.intern_repo = intern_repo or InternRepo()
        self.project_repo = project_repo or ProjectRepo()
        self.user_repo = user_repo or UserRepo()
        self.mail_service = mail_service or MailService()
        self.permission_repo = permission_repo or PermissionRepo()

        self.notifier = NotificationService(
            notification_repo=self.notification_repo,
            mail_service=self.mail_service
        )

    def get_all_feedback(self):
        items = self.feedback_repo.get_all()
        return [f.to_dict() for f in items]

    def mentor_give_feedback_to_intern(self, user_id: int, data: dict):
        self.permission_repo.ensure(user_id, "EVALUATE_INTERN")

        intern_id = data.get("intern_id")
        score = data.get("score")
        comment = data.get("comment") or ""

        if intern_id is None:
            raise ValueError("intern_id is required")
        if score is None:
            raise ValueError("score is required")

        intern = self.intern_repo.get_by_id(intern_id)
        mentor = self.user_repo.get_by_id(user_id)

        if not intern:
            raise ValueError("Intern not found")

        existing = self.feedback_repo.get_by_user_and_intern(user_id, intern_id)

        if existing:
            fb = self.feedback_repo.update(existing.id, {
                "score": score,
                "comment": comment
            })
            created = False
        else:
            fb = self.feedback_repo.create({
                "from_user_id": user_id,
                "to_intern_id": intern_id,
                "score": score,
                "comment": comment,
                "type": FeedbackType.TRAINER_INTERN,
                "created_at": datetime.utcnow()
            })
            created = True

        # Notify intern
        if intern.user_id:
            title = (
                "New Intern Evaluation"
                if created else
                "Intern Evaluation Updated"
            )
            message = f"You received {score}/10 from {mentor.username}."

            self.notifier.notify_user(
                user_id=intern.user_id,
                title=title,
                message=message,
                type="FEEDBACK_INTERN",
                link_url="/feedbacks",
                send_email=True
            )

        # Notify mentor (self notify)
        self.notifier.notify_user(
            user_id=user_id,
            title="Feedback Submitted",
            message=f"You evaluated intern {intern.name} with {score}/10.",
            type="FEEDBACK_SELF",
            link_url="/feedbacks",
            send_email=False
        )

        return fb.to_dict()

    def intern_give_feedback_to_project(self, user_id: int, data: dict):
        intern = self.user_repo.get_by_id(user_id).intern_profile

        if not intern:
            raise PermissionError("You are not an intern")

        project_id = data.get("project_id")
        score = data.get("score")
        comment = data.get("comment") or ""

        if project_id is None:
            raise ValueError("project_id is required")
        if score is None:
            raise ValueError("score is required")

        project = self.project_repo.get_by_id(project_id)

        if not project:
            raise ValueError("Project not found")

        existing = self.feedback_repo.get_by_user_and_project(user_id, project_id)

        if existing:
            fb = self.feedback_repo.update(existing.id, {
                "score": score,
                "comment": comment,
            })
            created = False
        else:
            fb = self.feedback_repo.create({
                "from_user_id": user_id,
                "to_intern_id": intern.id,
                "to_project_id": project_id,
                "score": score,
                "comment": comment,
                "type": FeedbackType.INTERN_PROJECT,
                "created_at": datetime.utcnow()
            })
            created = True

        receivers = set()

        if getattr(project, "owner_id", None):
            receivers.add(project.owner_id)

        if getattr(project, "mentor_id", None):
            receivers.add(project.mentor_id)

        title = "New Feedback on Project" if created else "Project Feedback Updated"
        message = f"{intern.name} rated project '{project.title}' {score}/10."

        for uid in receivers:
            self.notifier.notify_user(
                user_id=uid,
                title=title,
                message=message,
                type="FEEDBACK_PROJECT",
                link_url=f"/projects/{project_id}",
                send_email=True
            )

        # Self notify
        self.notifier.notify_user(
            user_id=user_id,
            title="Feedback Submitted",
            message=f"You rated project '{project.title}' {score}/10.",
            type="FEEDBACK_SELF",
            link_url=f"/projects/{project_id}",
            send_email=False
        )

        return fb.to_dict()

    def mentor_give_feedback_to_project(self, mentor_id: int, data: dict):
        self.permission_repo.ensure(mentor_id, "EVALUATE_PROJECT")

        project_id = data.get("project_id")
        score = data.get("score")
        comment = data.get("comment") or ""

        if project_id is None:
            raise ValueError("project_id is required")
        if score is None:
            raise ValueError("score is required")

        project = self.project_repo.get_by_id(project_id)

        fb = self.feedback_repo.create({
            "from_user_id": mentor_id,
            "to_project_id": project_id,
            "score": score,
            "comment": comment,
            "type": FeedbackType.TRAINER_PROJECT,
            "created_at": datetime.utcnow()
        })

        mentor = self.user_repo.get_by_id(mentor_id)

        receivers = set()

        if getattr(project, "owner_id", None):
            receivers.add(project.owner_id)

        if getattr(project, "mentor_id", None):
            receivers.add(project.mentor_id)

        title = "New Project Evaluation"
        message = f"{mentor.username} evaluated project '{project.title}' with {score}/10."

        for uid in receivers:
            self.notifier.notify_user(
                user_id=uid,
                title=title,
                message=message,
                type="FEEDBACK_PROJECT",
                link_url=f"/projects/{project_id}",
                send_email=True
            )

        # Self notify
        self.notifier.notify_user(
            user_id=mentor_id,
            title="Feedback Submitted",
            message=f"You evaluated project '{project.title}' with {score}/10.",
            type="FEEDBACK_SELF",
            link_url=f"/projects/{project_id}",
            send_email=False
        )

        return fb.to_dict()

    def get_feedback_for_intern(self, requester_id: int, intern_id: int):
        return [f.to_dict() for f in self.feedback_repo.get_for_intern(intern_id)]

    def get_feedback_for_project(self, requester_id: int, project_id: int):
        return [f.to_dict() for f in self.feedback_repo.get_for_project(project_id)]

    def update_feedback(self, user_id: int, feedback_id: int, data: dict):
        fb = self.feedback_repo.get_by_id(feedback_id)

        if not fb:
            raise ValueError("Feedback not found")

        if fb.from_user_id != user_id:
            raise PermissionError("You can only update your own feedback")

        updated = self.feedback_repo.update(feedback_id, data)

        targets = self._get_feedback_target_user_ids(updated)

        for uid in targets:
            self.notifier.notify_user(
                user_id=uid,
                title="Feedback Updated",
                message="A feedback related to you has been updated.",
                type="FEEDBACK_UPDATE",
                link_url="/feedbacks",
                send_email=True
            )

        self.notifier.notify_user(
            user_id=user_id,
            title="Feedback Updated",
            message="You updated your feedback.",
            type="FEEDBACK_SELF",
            link_url="/feedbacks",
            send_email=False
        )

        return updated.to_dict()

    def delete_feedback(self, user_id: int, feedback_id: int):
        self.permission_repo.ensure(user_id, "FEEDBACK_DELETE")

        fb = self.feedback_repo.get_by_id(feedback_id)

        if not fb:
            raise ValueError("Feedback not found")

        targets = self._get_feedback_target_user_ids(fb)

        deleted = self.feedback_repo.soft_delete(feedback_id)

        if deleted:
            for uid in targets:
                self.notifier.notify_user(
                    user_id=uid,
                    title="Feedback Deleted",
                    message="A feedback related to you has been removed.",
                    type="FEEDBACK_DELETE",
                    link_url="/feedbacks",
                    send_email=True
                )

            self.notifier.notify_user(
                user_id=user_id,
                title="Feedback Deleted",
                message="You removed a feedback.",
                type="FEEDBACK_SELF",
                link_url="/feedbacks",
                send_email=False
            )

        return True if deleted else False

    def _get_feedback_target_user_ids(self, fb):
        ids = set()

        if fb.to_intern_id:
            intern = self.intern_repo.get_by_id(fb.to_intern_id)
            if intern and intern.user_id:
                ids.add(intern.user_id)

        if fb.to_project_id:
            project = self.project_repo.get_by_id(fb.to_project_id)

            if getattr(project, "owner_id", None):
                ids.add(project.owner_id)

            if getattr(project, "mentor_id", None):
                ids.add(project.mentor_id)

        return list(ids)
