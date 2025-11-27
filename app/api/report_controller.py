from flask import Blueprint, request, send_file, jsonify, g
from app.utils.uc_provider import provide_report_uc
from app.utils.auth_middleware import require_auth
import io

report_bp = Blueprint("report_bp", __name__, url_prefix="/api/reports")


@report_bp.route("/export", methods=["POST"])
@require_auth
def export_report():
    uc = provide_report_uc()
    user = g.current_user

    try:
        payload = request.get_json() or {}
        binary = uc.export_report(user.id, payload)

        return send_file(
            io.BytesIO(binary),
            download_name=f"report_{payload.get('type', 'data')}.xlsx",
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        print("EXPORT ERROR:", e)
        return jsonify({"error": str(e)}), 500


@report_bp.route("/statistics", methods=["GET"])
@require_auth
def statistics():
    uc = provide_report_uc()
    user = g.current_user

    try:
        params = {
            "from_date": request.args.get("from_date"),
            "to_date": request.args.get("to_date"),
            "major": request.args.get("major"),
            "status": request.args.get("status")
        }
        result = uc.get_statistics(user.id, params)
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        print("STATISTICS ERROR:", e)
        return jsonify({"error": str(e)}), 500


@report_bp.route("/view", methods=["GET"])
@require_auth
def view_report():
    uc = provide_report_uc()
    user = g.current_user

    try:
        filters = {
            "type": request.args.get("type", "intern"),
            "from_date": request.args.get("from_date"),
            "to_date": request.args.get("to_date"),
            "major": request.args.get("major"),
            "status": request.args.get("status"),
            "intern_id": request.args.get("intern_id"),
            "project_id": request.args.get("project_id")
        }
        data = uc.view_report(user.id, filters)
        return jsonify([d.to_dict() for d in data]), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        print("VIEW REPORT ERROR:", e)
        return jsonify({"error": str(e)}), 500