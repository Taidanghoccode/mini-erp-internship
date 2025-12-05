from flask import Blueprint, render_template, abort, g
from app.utils.auth_middleware import load_user

from app.utils.uc_provider import (
    provide_intern_uc,
    provide_project_uc,
    provide_intern_project_uc,
    provide_user_uc,
    provide_training_plan_uc
)

from app.usecase.dashboard_uc import DashboardUC

web_bp = Blueprint(
    "web_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/web/static"
)


def load_context():
    try:
        user = load_user()
    except:
        user = None

    return {
        "current_user": user,
        "permissions": getattr(g, "current_permissions", []),
    }


@web_bp.route("/")
def dashboard():
    ctx = load_context()
    user = ctx["current_user"]

    uc = DashboardUC()
    data = uc.get_dashboard(user)

    return render_template(
        "dashboard.html",
        summary=data["summary"],
        intern_performance=data["intern_performance"],
        project_quality=data["project_quality"],
        activity_logs=data["activity_logs"],
    )

@web_bp.route("/interns")
def interns_page():
    ctx = load_context()

    if not ctx["current_user"]:
        return render_template("login.html")

    intern_uc = provide_intern_uc()
    ctx["interns"] = intern_uc.get_all_interns(ctx["current_user"].id)
    return render_template("interns.html", **ctx)


@web_bp.route("/interns/<int:id>")
def intern_detail(id):
    ctx = load_context()

    if not ctx["current_user"]:
        return render_template("login.html")

    intern_uc = provide_intern_uc()
    intern_project_uc = provide_intern_project_uc()

    intern = intern_uc.get_intern_by_id(ctx["current_user"].id, id)
    if not intern:
        abort(404)

    ctx.update({
        "intern": intern,
        "projects": intern_project_uc.get_projects_of_intern(ctx["current_user"].id, id)
    })
    return render_template("intern_detail.html", **ctx)


@web_bp.route("/projects")
def projects_page():
    ctx = load_context()

    if not ctx["current_user"]:
        return render_template("login.html")

    project_uc = provide_project_uc()
    ctx["projects"] = project_uc.get_all_projects(ctx["current_user"].id)
    return render_template("project.html", **ctx)


@web_bp.route("/projects/<int:id>")
def project_detail(id):
    ctx = load_context()

    if not ctx["current_user"]:
        return render_template("login.html")

    project_uc = provide_project_uc()
    intern_project_uc = provide_intern_project_uc()

    try:
        project = project_uc.get_project_by_id(ctx["current_user"].id, id)

        if not project:
            abort(404)

        ctx.update({
            "project": project,
            "interns": intern_project_uc.get_interns_of_project(ctx["current_user"].id, id)
        })
        return render_template("project_detail.html", **ctx)

    except PermissionError as e:
        return render_template("error.html", message=str(e)), 403

    except Exception as e:
        print("ERROR project_detail:", e)
        import traceback
        traceback.print_exc()
        return render_template("error.html", message="Something went wrong"), 500


@web_bp.route("/users")
def users_page():
    ctx = load_context()

    if not ctx["current_user"]:
        return render_template("login.html")

    user_uc = provide_user_uc()
    ctx["users"] = user_uc.get_all_users(ctx["current_user"].id)
    return render_template("users.html", **ctx)


@web_bp.route("/users/<int:id>")
def user_detail(id):
    ctx = load_context()

    if not ctx["current_user"]:
        return render_template("login.html")

    user_uc = provide_user_uc()
    target = user_uc.get_user_by_id(ctx["current_user"].id, id)
    if not target:
        abort(404)

    ctx["user"] = target
    return render_template("user_detail.html", **ctx)


@web_bp.route("/feedbacks")
def feedbacks_page():
    return render_template("feedbacks.html", **load_context())


@web_bp.route("/roles")
def roles_page():
    return render_template("roles.html", **load_context())


@web_bp.route("/report")
def report_page():
    return render_template("report.html", **load_context())


@web_bp.route("/training-plans")
def training_plans_page():
    ctx = load_context()

    if not ctx["current_user"]:
        return render_template("login.html")

    training_uc = provide_training_plan_uc()
    
    role_code = ctx["current_user"].role.code if ctx["current_user"].role else None
    ctx["plans"] = training_uc.get_all_plans(ctx["current_user"].id, role_code)
    
    return render_template("training_plan.html", **ctx)


@web_bp.route("/training-plans/<int:id>")
def training_plan_detail(id):
    ctx = load_context()

    if not ctx["current_user"]:
        return render_template("login.html")

    training_uc = provide_training_plan_uc()
    role_code = ctx["current_user"].role.code if ctx["current_user"].role else None

    try:
        plan_dict = training_uc.get_plan_by_id(ctx["current_user"].id, id, role_code)

        ctx.update({
            "plan": plan_dict,
            "intern": plan_dict.get("intern")
        })

        return render_template("training_plan_detail.html", **ctx)

    except PermissionError:
        return render_template("error.html", message="You don't have permission"), 403
    except ValueError:
        abort(404)
    except Exception as e:
        print("ERROR training_plan_detail:", e)
        import traceback
        traceback.print_exc()
        abort(500)


@web_bp.route("/login")
def login_page():
    return render_template("login.html")


@web_bp.route("/profile")
def profile_page():
    return render_template("profile.html", **load_context())


@web_bp.route("/settings")
def settings_page():
    return render_template("settings.html", **load_context())


@web_bp.route("/settings/activity-logs")
def settings_activity_logs_page():
    return render_template("settings_activity_logs.html", **load_context())