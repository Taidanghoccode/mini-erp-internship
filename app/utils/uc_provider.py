from app.usecase.user_uc import UserUC
from app.usecase.role_uc import RoleUC
from app.usecase.permission_uc import PermissionUC
from app.usecase.feedback_uc import FeedbackUC
from app.usecase.intern_uc import InternUC
from app.usecase.project_uc import ProjectUC
from app.usecase.intern_project_uc import InternProjectUC
from app.usecase.report_uc import ReportUC
from app.usecase.training_plan_uc import TrainingPlanUC
from app.usecase.activitylog_uc import ActivityLogUC
from app.usecase.auth_uc import AuthUC

from app.repo.user_repo import UserRepo
from app.repo.role_repo import RoleRepo
from app.repo.permission_repo import PermissionRepo
from app.repo.feedback_repo import FeedbackRepo
from app.repo.intern_repo import InternRepo
from app.repo.project_repo import ProjectRepo
from app.repo.intern_project_repo import InternProjectRepo
from app.repo.training_plan_repo import TrainingPlanRepo
from app.repo.activitylog_repo import ActivityLogRepo

def provide_user_uc():
    return UserUC(
        user_repo=UserRepo(),
        role_repo=RoleRepo(),
        permission_repo=PermissionRepo(),
        activitylog_uc=ActivityLogUC()
    )


def provide_role_uc():
    return RoleUC(
        role_repo=RoleRepo(),
        permission_repo=PermissionRepo(),
        activitylog_uc=ActivityLogUC()
    )


def provide_permission_uc():
    return PermissionUC(
        permission_repo=PermissionRepo(),
        activitylog_uc=ActivityLogUC()
    )


def provide_feedback_uc():
    return FeedbackUC(
        feedback_repo=FeedbackRepo(),
        permission_repo=PermissionRepo(),
        activitylog_uc=ActivityLogUC()
    )


def provide_intern_uc():
    return InternUC(
        intern_repo=InternRepo(),
        intern_project_repo=InternProjectRepo(),
        activitylog_uc=ActivityLogUC()
    )


def provide_project_uc():
    return ProjectUC(
        project_repo=ProjectRepo(),
        activitylog_uc=ActivityLogUC()
    )


def provide_intern_project_uc():
    return InternProjectUC(
        intern_project_repo=InternProjectRepo(),
        intern_repo=InternRepo(),
        project_repo=ProjectRepo(),
        permission_repo=PermissionRepo(),
        activitylog_uc=ActivityLogUC()
    )


def provide_report_uc():
    return ReportUC(
        intern_repo=InternRepo(),
        project_repo=ProjectRepo(),
        feedback_repo=FeedbackRepo(),
        permission_repo=PermissionRepo()
    )


def provide_training_plan_uc():
    return TrainingPlanUC(
        training_plan_repo=TrainingPlanRepo(),
        permission_repo=PermissionRepo(),
        activitylog_uc=ActivityLogUC()
    )
def provide_auth_uc():
    return AuthUC(
        user_repo=UserRepo(), 
        permission_repo= PermissionRepo()
    )

def provide_activitylog_uc():
    return ActivityLogUC(ActivityLogRepo())