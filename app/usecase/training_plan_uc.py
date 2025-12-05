from app.interfaces.tranining_plan_port import TrainingPlanRepoInterface
from app.repo.permission_repo import PermissionRepo
from app.repo.user_repo import UserRepo
from app.repo.intern_repo import InternRepo
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
        self._check(user_id, "TRAININGPLAN_CREATE")

        data['created_by'] = user_id
        plan = self.training_plan_repo.create(data)

        self.activitylog_uc.log_action(
            user_id, "CREATE_TRAINING_PLAN",
            f"Created training plan {plan.id}"
        )
        return plan

    def get_all_plans(self, user_id, role_code):
        if role_code == "INTERN":
            user = UserRepo().get_by_id(user_id)
            intern = user.intern_profile if user else None

            if not intern:
                return []

            return self.training_plan_repo.get_for_intern(intern.id)

        self._check(user_id, "TRAININGPLAN_VIEW")
        return self.training_plan_repo.get_all()

    def get_plan_by_id(self, user_id, plan_id, role_code):
        plan = self.training_plan_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError("Training plan not found")

        if role_code == "INTERN":
            user = UserRepo().get_by_id(user_id)
            intern = user.intern_profile if user else None

            if not intern or plan.intern_id != intern.id:
                raise PermissionError("You cannot view another intern's training plan.")
        else:
            self._check(user_id, "TRAININGPLAN_VIEW")

        plan_dict = plan.to_dict()

        intern = InternRepo().get_by_id(plan.intern_id) if plan.intern_id else None
        plan_dict["intern"] = intern.to_dict() if intern else None

        creator = UserRepo().get_by_id(plan.created_by)
        plan_dict["created_by_name"] = creator.username if creator else None

        return plan_dict

    def update_training_plan(self, user_id, plan_id, data):
        user = UserRepo().get_by_id(user_id)
        role = user.role.code if user and user.role else None 

        plan = self.training_plan_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError("Training plan not found")
        
        if role == "INTERN":
            intern = user.intern_profile
            if not intern or plan.intern_id != intern.id:
                raise PermissionError("You cannot edit")
            
            new_progress = data.get("progress", None)
            if new_progress is None:
                raise PermissionError("Intern can only update progress")
            if not (0<=int(new_progress)<=100):
                raise ValueError("Progress must be between 0 and 100")

            updated = self.training_plan_repo.update(plan_id, {"progress": new_progress})

            self.activitylog_uc.log_action(
                user_id,
                "UPDATE_PROGRESS",
                f"Intern updated progress to {new_progress}%"
            )

            return updated

        #self._check(user_id, "TRAININGPLAN_UPDATE")

        if 'created_by' in data:
            del data['created_by']

        updated = self.training_plan_repo.update(plan_id, data)

        self.activitylog_uc.log_action(
            user_id,
            "UPDATE_TRAINING_PLAN",
            f"Updated training plan {plan_id}"
        )

        return updated
    
    def delete_training_plan(self, user_id, plan_id):
        self._check(user_id, "TRAININGPLAN_DELETE")

        ok = self.training_plan_repo.delete(plan_id)
        if not ok:
            raise ValueError("Training plan not found")

        self.activitylog_uc.log_action(
            user_id, "DELETE_TRAINING_PLAN",
            f"Deleted training plan {plan_id}"
        )
        return True
