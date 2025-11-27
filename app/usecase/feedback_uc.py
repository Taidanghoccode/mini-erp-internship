from app.repo.feedback_repo import FeedbackRepo
from app.repo.intern_repo import InternRepo
from app.repo.project_repo import ProjectRepo
from app.repo.permission_repo import PermissionRepo
from app.usecase.activitylog_uc import ActivityLogUC
from app.utils.notification_service import NotificationService
from app.utils.exception import NotFound, BadRequest
from app.models.feedback import FeedbackType


class FeedbackUC:
    def __init__(
        self,
        feedback_repo: FeedbackRepo | None = None,
        intern_repo: InternRepo | None = None,
        project_repo: ProjectRepo | None = None,
        permission_repo: PermissionRepo | None = None,
        activitylog_uc: ActivityLogUC | None = None,
        notification_service: NotificationService | None = None,
    ):
        self.feedback_repo = feedback_repo or FeedbackRepo()
        self.intern_repo = intern_repo or InternRepo()
        self.project_repo = project_repo or ProjectRepo()
        self.permission_repo = permission_repo or PermissionRepo()
        self.activitylog_uc = activitylog_uc or ActivityLogUC()
        self.notification_service = notification_service or NotificationService()

    def _require(self, user_id: int, perm_code: str):
        self.permission_repo.ensure(user_id, perm_code)

    def intern_give_feedback_to_project(self, user_id: int, data: dict):
        self._require(user_id, "FEEDBACK_CREATE_PROJECT")

        score = data.get("rating") or data.get("score")
        intern_id = data.get("intern_id")
        project_id = data.get("project_id")

        if not intern_id or not project_id or score is None:
            raise BadRequest("Missing intern_id, project_id or score")

        intern = self.intern_repo.get_by_id(intern_id)
        if not intern:
            raise NotFound("Intern not found")

        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFound("Project not found")

        fb = self.feedback_repo.create({
            "type": FeedbackType.INTERN_PROJECT,
            "score": score,
            "comment": data.get("comment"),
            "from_user_id": user_id,
            "to_intern_id": None,
            "to_project_id": project_id
        })

        self.notification_service.notify_user(
            project.created_by if hasattr(project, "created_by") else user_id,
            "New Project Rating",
            f"Your project received a new rating: {score} stars.",
            type="feedback"
        )

        return fb.to_dict()

    def mentor_give_feedback_to_intern(self, user_id: int, data: dict):
        self._require(user_id, "EVALUATE_INTERN")

        score = data.get("rating") or data.get("score")
        intern_id = data.get("intern_id")

        if not intern_id or score is None:
            raise BadRequest("Missing intern_id or score")

        intern = self.intern_repo.get_by_id(intern_id)
        if not intern:
            raise NotFound("Intern not found")

        fb = self.feedback_repo.create({
            "type": FeedbackType.TRAINER_INTERN,
            "score": score,
            "comment": data.get("comment"),
            "from_user_id": user_id,
            "to_intern_id": intern_id,
            "to_project_id": None
        })

        self.notification_service.notify_user(
            intern.user_id if hasattr(intern, "user_id") else intern_id,
            "New Intern Evaluation",
            f"You received a new evaluation: {score} points.",
            type="feedback"
        )

        return fb.to_dict()

    def mentor_give_feedback_to_project(self, user_id: int, data: dict):
        self._require(user_id, "EVALUATE_PROJECT")

        score = data.get("rating") or data.get("score")
        project_id = data.get("project_id")

        if not project_id or score is None:
            raise BadRequest("Missing project_id or score")

        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFound("Project not found")

        fb = self.feedback_repo.create({
            "type": FeedbackType.TRAINER_PROJECT,
            "score": score,
            "comment": data.get("comment"),
            "from_user_id": user_id,
            "to_intern_id": None,
            "to_project_id": project_id
        })

        self.notification_service.notify_user(
            project.created_by if hasattr(project, "created_by") else user_id,
            "New Project Evaluation",
            f"Your project received a new evaluation: {score} points.",
            type="feedback"
        )

        return fb.to_dict()

    def get_feedback_for_intern(self, user_id: int, intern_id: int):
        self._require(user_id, "FEEDBACK_VIEW")

        intern = self.intern_repo.get_by_id(intern_id)
        if not intern:
            raise NotFound("Intern not found")

        items = self.feedback_repo.get_for_intern(intern_id)
        return [f.to_dict() for f in items]

    def get_feedback_for_project(self, user_id: int, project_id: int):
        self._require(user_id, "FEEDBACK_VIEW")

        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFound("Project not found")

        items = self.feedback_repo.get_for_project(project_id)
        return [f.to_dict() for f in items]

    def update_feedback(self, user_id: int, feedback_id: int, data: dict):
        self._require(user_id, "FEEDBACK_CREATE_PROJECT")

        fb = self.feedback_repo.get_by_id(feedback_id)
        if not fb:
            raise NotFound("Feedback not found")

        score = data.get("score")
        comment = data.get("comment")

        if score is None:
            raise BadRequest("Missing score")

        updated = self.feedback_repo.update(feedback_id, {
            "score": score,
            "comment": comment
        })

        return updated.to_dict()

    def delete_feedback(self, user_id: int, feedback_id: int):
        self._require(user_id, "FEEDBACK_DELETE")

        fb = self.feedback_repo.get_by_id(feedback_id)
        if not fb:
            raise NotFound("Feedback not found")

        self.feedback_repo.delete(feedback_id)
        return True
