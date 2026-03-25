import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from utils.ai_helper import explain_with_ai, is_ai_available
from utils.solver import SolverError, solve_with_laplace

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

    @app.route("/", methods=["GET", "POST"])
    def index():
        form_data = {
            "equation": "",
            "y0": "",
            "y1": "",
            "ai_mode": False,
        }
        result = None
        error = None

        if request.method == "POST":
            form_data = {
                "equation": request.form.get("equation", "").strip(),
                "y0": request.form.get("y0", "").strip(),
                "y1": request.form.get("y1", "").strip(),
                "ai_mode": request.form.get("ai_mode") == "on",
            }
            try:
                result = solve_with_laplace(
                    equation_text=form_data["equation"],
                    y0_text=form_data["y0"],
                    y1_text=form_data["y1"],
                )
            except SolverError as exc:
                error = str(exc)
            except Exception:
                error = (
                    "Ocurrió un error inesperado al procesar la ecuación. "
                    "Verifica el formato e inténtalo de nuevo."
                )

        return render_template(
            "index.html",
            form_data=form_data,
            result=result,
            error=error,
            ai_available=is_ai_available(),
        )

    @app.post("/api/ai-explain")
    def ai_explain():
        if not is_ai_available():
            return jsonify(
                {
                    "ok": False,
                    "message": (
                        "El Modo IA requiere configurar OPENAI_API_KEY en el servidor."
                    ),
                }
            ), 400

        payload = request.get_json(silent=True) or {}
        try:
            text = explain_with_ai(payload)
            return jsonify({"ok": True, "text": text})
        except Exception as exc:
            return jsonify(
                {
                    "ok": False,
                    "message": f"No se pudo generar la explicación con IA: {exc}",
                }
            ), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
