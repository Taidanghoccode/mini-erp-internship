from app.repo.intern_repo import InternRepo
from app.repo.project_repo import ProjectRepo
from app.repo.feedback_repo import FeedbackRepo
from app.repo.user_repo import UserRepo
from app.repo.activitylog_repo import ActivityLogRepo
from app.models.feedback import FeedbackType


class DashboardUC:
    def __init__(
        self,
        intern_repo=None,
        project_repo=None,
        feedback_repo=None,
        user_repo=None,
        activity_repo=None
    ):
        self.intern_repo = intern_repo or InternRepo()
        self.project_repo = project_repo or ProjectRepo()
        self.feedback_repo = feedback_repo or FeedbackRepo()
        self.user_repo = user_repo or UserRepo()
        self.activity_repo = activity_repo or ActivityLogRepo()

    def get_summary(self):
        interns = self.intern_repo.get_all()
        projects = self.project_repo.get_all()
        feedbacks = self.feedback_repo.get_all()  # đã filter is_deleted=False
        users = self.user_repo.get_all()

        return {
            "total_interns": len(interns),
            "total_projects": len(projects),
            "total_feedbacks": len(feedbacks),
            "active_users": sum(1 for u in users if u.is_active),
        }

    def get_intern_performance(self):
        feedbacks = self.feedback_repo.get_all()  # all đều chưa deleted
        interns = self.intern_repo.get_all()

        intern_rating_map = {}

        for fb in feedbacks:
            if fb.type == FeedbackType.TRAINER_INTERN and fb.to_intern_id is not None:
                intern_rating_map.setdefault(fb.to_intern_id, []).append(fb.score)

        intern_results = []
        for intern in interns:
            ratings = intern_rating_map.get(intern.id, [])
            avg = sum(ratings) / len(ratings) if ratings else 0

            intern_results.append({
                "id": intern.id,
                "name": intern.name,
                "email": intern.email,
                "average_rating": round(avg, 2),
                "feedback_count": len(ratings),
            })

        sorted_interns = sorted(intern_results, key=lambda x: x["average_rating"], reverse=True)

        valid_ratings = [i["average_rating"] for i in intern_results if i["feedback_count"] > 0]

        return {
            "average_intern_rating": round(
                sum(valid_ratings) / len(valid_ratings), 2
            ) if valid_ratings else 0,
            "top_interns": sorted_interns[:5],
            "low_interns": sorted_interns[-5:],
        }

    def get_project_quality(self):
        feedbacks = self.feedback_repo.get_all()  # CHỈ LẤY feedback chưa deleted
        projects = self.project_repo.get_all()

        project_rate_map = {}

        for fb in feedbacks:
            if fb.to_project_id is not None and fb.type in (
                FeedbackType.TRAINER_PROJECT,
                FeedbackType.INTERN_PROJECT
            ):
                project_rate_map.setdefault(fb.to_project_id, []).append(fb.score)

        project_results = []
        for project in projects:
            ratings = project_rate_map.get(project.id, [])
            avg = sum(ratings) / len(ratings) if ratings else 0

            project_results.append({
                "id": project.id,
                "title": project.title,
                "average_rating": round(avg, 2),
                "feedback_count": len(ratings),
                "status": project.status,
            })

        sorted_projects = sorted(project_results, key=lambda x: x["average_rating"], reverse=True)

        valid_ratings = [p["average_rating"] for p in project_results if p["feedback_count"] > 0]

        return {
            "average_project_rating": round(
                sum(valid_ratings) / len(valid_ratings), 2
            ) if valid_ratings else 0,
            "top_projects": sorted_projects[:5],
        }

    def get_recent_logs(self):
        logs = self.activity_repo.get_all()[:10]
        return [
            {
                "user": log.user.username if log.user else "System",
                "action": log.action,
                "details": log.details,
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for log in logs
        ]

    def get_dashboard(self, user):
        data = {
            "summary": self.get_summary(),
            "intern_performance": self.get_intern_performance(),
            "project_quality": self.get_project_quality(),
        }

        if user and user.role.code == "ADMIN":
            data["activity_logs"] = self.get_recent_logs()
        else:
            data["activity_logs"] = []

        return data
