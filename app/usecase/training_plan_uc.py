from app.interfaces.tranining_plan_port import TrainingPlanRepoInterface
from app.repo.permission_repo import PermissionRepo
from app.repo.user_repo import UserRepo
from app.usecase.activitylog_uc import ActivityLogUC


class TrainingPlanUC:
    def __init__(
        self, 
        training_plan_repo: TrainingPlanRepoInterface, 
        permission_repo: PermissionRepo, 
        activitylog_uc: ActivityLogUC
    ):
        self.training_plan_repo = training_plan_repo
        self.permission_repo = permission_repo
        self.activitylog_uc = activitylog_uc

    def _check(self, user_id, permission_code):
        if not self.permission_repo.user_has(user_id, permission_code):
            raise PermissionError(f"Missing permission: {permission_code}")


    def create_training_plan(self, user_id, data):
        try:
            self._check(user_id, "TRAININGPLAN_CREATE")
            data["created_by"] = user_id

            plan = self.training_plan_repo.create(data)


            self.activitylog_uc.log_action(
                user_id,
                "CREATE_TRAINING_PLAN",
                f"Created training plan {plan.id}"
            )
            return plan.to_dict()

        except Exception as e:
            print("DEBUG CREATE TRAINING PLAN ERROR:", e)
            raise
    
    def get_all_plans(self, user_id):
        user = UserRepo().get_by_id(user_id)
        role_code = user.role.code if user.role else None

        self._check(user_id, "TRAININGPLAN_VIEW")

        if role_code == "INTERN":
            intern = user.intern_profile
            if not intern:
                return []

            plans = self.training_plan_repo.get_for_intern(intern.id)
            return [p.to_dict() for p in plans]

        plans = self.training_plan_repo.get_all()
        return [p.to_dict() for p in plans]

    def get_plan_by_id(self, user_id, plan_id):
        plan = self.training_plan_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError("Training plan not found")

        user = UserRepo().get_by_id(user_id)
        role_code = user.role.code if user.role else None

        if role_code == "INTERN":
            intern = user.intern_profile
            if not intern or plan.intern_id != intern.id:
                raise PermissionError("You cannot view another intern's training plan.")
            return plan.to_dict()

        self._check(user_id, "TRAININGPLAN_VIEW")
        return plan.to_dict()

    def update_training_plan(self, user_id, plan_id, data):
        self._check(user_id, "TRAININGPLAN_UPDATE")

        plan = self.training_plan_repo.update(plan_id, data)
        if not plan:
            raise ValueError("Training plan not found")

        self.activitylog_uc.log_action(
            user_id,
            "UPDATE_TRAINING_PLAN",
            f"Updated training plan {plan_id}"
        )
        return plan.to_dict()

    def delete_training_plan(self, user_id, plan_id):
        self._check(user_id, "TRAININGPLAN_DELETE")

        ok = self.training_plan_repo.delete(plan_id)
        if not ok:
            raise ValueError("Training plan not found")

        self.activitylog_uc.log_action(
            user_id,
            "DELETE_TRAINING_PLAN",
            f"Deleted training plan {plan_id}"
        )
        return True
