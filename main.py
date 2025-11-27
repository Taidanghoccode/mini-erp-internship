from flask import Flask, jsonify, g , request
from app.db.db import db
from app.db.init_models import load_models    
from app.utils.token_service import decode_access_token
from app.repo.user_repo import UserRepo

from app.api.inter_controller import intern_bp
from app.api.project_controller import project_bp
from app.api.intern_project_controller import intern_project_bp
from app.api.user_controller import user_bp
from app.api.feedback_controller import feedback_bp
from app.api.role_controller import role_bp
from app.api.permission_controller import permission_bp
from app.api.report_controller import report_bp
from app.api.training_plan_controller import trainingplan_bp
from app.api.auth_controller import auth_bp
from app.api.notification_controller import notif_bp
from app.api.activitylog_controller import log_bp

from app.web.view import web_bp
from app.models.user import User
from app.utils.exception import AppException


def create_app():
    app = Flask(__name__, static_folder="static")

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:123456@localhost/erp_internship"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "my-super-secret"

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USERNAME"] = "your_email@gmail.com"
    app.config["MAIL_PASSWORD"] = "your_app_password"
    app.config["MAIL_FROM"] = "Mini ERP <your_email@gmail.com>"

    db.init_app(app)

    app.register_blueprint(intern_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(intern_project_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(permission_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(trainingplan_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(notif_bp)
    app.register_blueprint(log_bp)

    
    user_repo = UserRepo()

    @app.before_request
    def load_current_user():
        g.current_user = None
        g.current_permissions = []

        token = None

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

        if not token:
            token = request.cookies.get("access_token")

        if not token:
            return 

        try:
            payload = decode_access_token(token)
            user = user_repo.get_by_id(payload.get("sub"))

            g.current_user = user
            g.current_permissions = payload.get("permissions", [])

        except Exception:
            g.current_user = None
            g.current_permissions = []


    @app.context_processor
    def inject_permissions():
        user = getattr(g, "current_user", None)
        perms = getattr(g, "current_permissions", [])
        return dict(current_user=user, permissions=perms)


    @app.errorhandler(AppException)
    def handle_app_exception(err):
        return jsonify(err.to_dict()), err.status_code

    @app.route("/api")
    def home():
        return {"message": "Mini ERP Internship Management API is running 🚀"}

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():

        load_models()
        db.create_all()
        print("Database tables created successfully.")

        print("\n" + "=" * 60)
        print("REGISTERED ROUTES:")
        print("=" * 60)
        for rule in app.url_map.iter_rules():
            methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
            print(f"{rule.endpoint:40s} {methods:15s} {rule.rule}")
        print("=" * 60 + "\n")

    app.run(debug=True)
