from flask import Blueprint, request, jsonify, g
from app.utils.uc_provider import provide_training_plan_uc
from app.utils.auth_middleware import require_auth, require_permission
from sqlalchemy.orm import joinedload
from app.models.training_plan import TrainingPlan

training_plan_bp = Blueprint("training_plan_bp", __name__, url_prefix="/api/training-plans")


@training_plan_bp.route("/", methods=["GET"])
@require_auth
def get_all_plans():
    try:
        uc = provide_training_plan_uc()
        plans = uc.get_all_plans(g.current_user.id, g.current_user.role.code)
        
        plan_ids = [p.id for p in plans]
        
        if not plan_ids:
            return jsonify([]), 200
        
        plans_with_relations = TrainingPlan.query.options(
            joinedload(TrainingPlan.intern),
            joinedload(TrainingPlan.creator)
        ).filter(TrainingPlan.id.in_(plan_ids)).all()
        
        result = []
        for plan in plans_with_relations:
            plan_dict = plan.to_dict()
            plan_dict['intern_name'] = plan.intern.name if plan.intern else None
            plan_dict['created_by_name'] = plan.creator.username if plan.creator else None
            result.append(plan_dict)
        
        return jsonify(result), 200
        
    except Exception as e:
        print("ERROR get_all_plans:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500


@training_plan_bp.route("/<int:plan_id>", methods=["GET"])
@require_auth
def get_plan(plan_id):
    try:
        uc = provide_training_plan_uc()
        role_code = g.current_user.role.code if g.current_user.role else None
        plan = uc.get_plan_by_id(g.current_user.id, plan_id, role_code)
        
        if not plan:
            return jsonify({"error": "Plan not found"}), 404
        
        plan = TrainingPlan.query.options(
            joinedload(TrainingPlan.intern),
            joinedload(TrainingPlan.creator)
        ).filter(TrainingPlan.id == plan_id).first()
        
        plan_dict = plan.to_dict()
        plan_dict['intern_name'] = plan.intern.name if plan.intern else None
        plan_dict['created_by_name'] = plan.creator.username if plan.creator else None
        
        if plan.intern:
            plan_dict['intern_details'] = {
                'id': plan.intern.id,
                'name': plan.intern.name,
                'email': plan.intern.email,
                'university': plan.intern.university,
                'major': plan.intern.major,
                'start_date': plan.intern.start_date.isoformat() if plan.intern.start_date else None,
                'end_date': plan.intern.end_date.isoformat() if plan.intern.end_date else None,
            }
        else:
            plan_dict['intern_details'] = None
        
        return jsonify(plan_dict), 200
        
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print("ERROR get_plan:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500


@training_plan_bp.route("/", methods=["POST"])
@require_auth
@require_permission("TRAININGPLAN_CREATE")
def create_plan():
    try:
        data = request.get_json() or {}
        
        uc = provide_training_plan_uc()
        plan = uc.create_training_plan(g.current_user.id, data)
        
        plan = TrainingPlan.query.options(
            joinedload(TrainingPlan.intern),
            joinedload(TrainingPlan.creator)
        ).filter(TrainingPlan.id == plan.id).first()
        
        plan_dict = plan.to_dict()
        plan_dict['intern_name'] = plan.intern.name if plan.intern else None
        plan_dict['created_by_name'] = plan.creator.username if plan.creator else None
        
        return jsonify(plan_dict), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print("ERROR create_plan:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500


@training_plan_bp.route("/<int:plan_id>", methods=["PUT"])
@require_auth
def update_plan(plan_id):
    try:
        data = request.get_json() or {}
        
        uc = provide_training_plan_uc()
        plan = uc.update_training_plan(g.current_user.id, plan_id, data)
        
        plan = TrainingPlan.query.options(
            joinedload(TrainingPlan.intern),
            joinedload(TrainingPlan.creator)
        ).filter(TrainingPlan.id == plan_id).first()
        
        plan_dict = plan.to_dict()
        plan_dict['intern_name'] = plan.intern.name if plan.intern else None
        plan_dict['created_by_name'] = plan.creator.username if plan.creator else None
        
        return jsonify(plan_dict), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        print("ERROR update_plan:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500


@training_plan_bp.route("/<int:plan_id>", methods=["DELETE"])
@require_auth
@require_permission("TRAININGPLAN_DELETE")
def delete_plan(plan_id):
    try:
        uc = provide_training_plan_uc()
        uc.delete_training_plan(g.current_user.id, plan_id)
        
        return jsonify({"message": "Training plan deleted successfully"}), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        print("ERROR delete_plan:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500