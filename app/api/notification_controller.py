from flask import Blueprint, request, jsonify, g
from app.utils.auth_middleware import require_auth
from app.usecase.notification_uc import NotificationUC

notif_uc = NotificationUC()
notif_bp = Blueprint("notif_bp", __name__, url_prefix="/api/notifications")

@notif_bp.route("/", methods=["GET"])
@require_auth
def list_notifications():
    only_unread = request.args.get("unread", "false").lower() == "true"
    items = notif_uc.list_for_user(g.current_user.id, only_unread)
    return jsonify(items), 200

@notif_bp.route("/<int:id>/read", methods=["PUT"])
@require_auth
def mark_read(id):
    ok = notif_uc.mark_read(g.current_user.id, id)
    return jsonify({"success": ok}), 200

@notif_bp.route("/read-all", methods=["PUT"])
@require_auth
def mark_all():
    count = notif_uc.mark_all_read(g.current_user.id)
    return jsonify({"read": count}), 200
