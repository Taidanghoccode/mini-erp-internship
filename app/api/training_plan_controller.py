from flask import Blueprint, request, jsonify, g
from app.utils.uc_provider import provide_training_plan_uc
from app.utils.auth_middleware import require_auth

trainingplan_bp = Blueprint("trainingplan_bp", __name__, url_prefix="/api/training-plans")


@trainingplan_bp.route("/", methods=["POST"])
@require_auth
def create_plan():
    uc = provide_training_plan_uc()
    user = g.current_user

    try:
        data = request.get_json() or {}
        plan = uc.create_training_plan(user.id, data)
        return jsonify(plan), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trainingplan_bp.route("/", methods=["GET"])
@require_auth
def get_all_plans():
    uc = provide_training_plan_uc()
    user = g.current_user

    try:
        plans = uc.get_all_plans(user.id)
        return jsonify(plans), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trainingplan_bp.route("/<int:plan_id>", methods=["GET"])
@require_auth
def get_plan(plan_id):
    uc = provide_training_plan_uc()
    user = g.current_user

    try:
        plan = uc.get_plan_by_id(user.id, plan_id)
        return (jsonify(plan), 200) if plan else (jsonify({"error": "Training plan not found"}), 404)
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trainingplan_bp.route("/<int:plan_id>", methods=["PUT"])
@require_auth
def update_plan(plan_id):
    uc = provide_training_plan_uc()
    user = g.current_user

    try:
        data = request.get_json() or {}
        updated = uc.update_training_plan(user.id, plan_id, data)
        return (jsonify(updated), 200) if updated else (jsonify({"error": "Training plan not found"}), 404)
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trainingplan_bp.route("/<int:plan_id>", methods=["DELETE"])
@require_auth
def delete_plan(plan_id):
    uc = provide_training_plan_uc()
    user = g.current_user

    try:
        deleted = uc.delete_training_plan(user.id, plan_id)
        return (jsonify({"deleted": deleted}), 200) if deleted else (jsonify({"error": "Training plan not found"}), 404)
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500
