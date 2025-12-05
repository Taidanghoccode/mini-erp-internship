from flask import Blueprint, request, jsonify, g
from app.utils.auth_middleware import require_auth
from app.utils.uc_provider import provide_feedback_uc

feedback_bp = Blueprint("feedback_bp", __name__, url_prefix="/api/feedback")

@feedback_bp.route("/all", methods=["GET"])
@require_auth
def get_all():
    uc = provide_feedback_uc()
    user = g.current_user
    items = uc.feedback_repo.get_all()
    return jsonify([f.to_dict() for f in items]), 200

@feedback_bp.route("/trainer/intern", methods=["POST"])
@require_auth
def trainer_evaluate_intern():
    uc = provide_feedback_uc()
    user = g.current_user
    data = request.get_json()
    try:
        fb = uc.mentor_give_feedback_to_intern(user.id, data)
        return jsonify(fb), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403

@feedback_bp.route("/intern/project", methods=["POST"])
@require_auth
def intern_feedback_project():
    uc = provide_feedback_uc()
    user = g.current_user
    data = request.get_json()
    try:
        fb = uc.intern_give_feedback_to_project(user.id, data)
        return jsonify(fb), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403

@feedback_bp.route("/trainer/project", methods=["POST"])
@require_auth
def trainer_evaluate_project():
    uc = provide_feedback_uc()
    user = g.current_user
    data = request.get_json()
    try:
        fb = uc.mentor_give_feedback_to_project(user.id, data)
        return jsonify(fb), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403

@feedback_bp.route("/intern/<int:intern_id>", methods=["GET"])
@require_auth
def get_feedback_for_intern(intern_id):
    uc = provide_feedback_uc()
    user = g.current_user
    try:
        result = uc.get_feedback_for_intern(user.id, intern_id)
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403

@feedback_bp.route("/project/<int:project_id>", methods=["GET"])
@require_auth
def get_feedback_for_project(project_id):
    uc = provide_feedback_uc()
    user = g.current_user
    try:
        result = uc.get_feedback_for_project(user.id, project_id)
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403

@feedback_bp.route("/<int:feedback_id>", methods=["PUT"])
@require_auth
def update_feedback(feedback_id):
    uc = provide_feedback_uc()
    user = g.current_user
    data = request.get_json()
    try:
        fb = uc.update_feedback(user.id, feedback_id, data)
        return jsonify(fb), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403

@feedback_bp.route("/<int:feedback_id>", methods=["DELETE"])
@require_auth
def delete_feedback(feedback_id):
    uc = provide_feedback_uc()
    user = g.current_user
    try:
        ok = uc.delete_feedback(user.id, feedback_id)
        return jsonify({"deleted": ok}), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
