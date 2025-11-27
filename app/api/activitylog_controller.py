from flask import Blueprint, jsonify, g
from app.utils.uc_provider import provide_activitylog_uc
from app.utils.auth_middleware import require_auth, require_permission

log_bp = Blueprint("log_bp", __name__, url_prefix="/api/activity-logs")

@log_bp.route("/", methods=["GET"])
@require_auth
def get_all_logs():
    uc = provide_activitylog_uc()

    # admin mới xem toàn bộ log
    if "USER_MANAGE" not in g.current_permissions:
        return jsonify({"error": "Permission denied"}), 403

    logs = uc.get_all_logs()
    return jsonify(logs), 200


@log_bp.route("/<int:log_id>", methods=["DELETE"])
@require_auth
@require_permission("USER_MANAGE")
def delete_log(log_id):
    uc = provide_activitylog_uc()
    ok = uc.delete_log(log_id)
    return jsonify({"deleted": ok}), 200
