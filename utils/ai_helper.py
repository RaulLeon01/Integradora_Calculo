from __future__ import annotations

import os

from openai import OpenAI


def is_ai_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def build_prompt(payload: dict) -> str:
    conditions = payload.get("conditions") or []
    conditions_block = "\\n".join(f"- {item}" for item in conditions) if conditions else "- Sin datos"

    return f"""
Explica en español, de forma clara y breve, la resolución por transformada de Laplace.
No inventes pasos que no aparezcan en los datos. Si falta un dato, dilo.

Datos del ejercicio:
- Orden: {payload.get('order')}
- Ecuación: {payload.get('equation')}
- Condiciones iniciales:
{conditions_block}
- Transformada de la ecuación: {payload.get('transform')}
- Solución en Laplace: {payload.get('ys')}
- Solución final: {payload.get('solution')}

Quiero que respondas con este formato:
1. Qué se hizo
2. Interpretación de Y(s)
3. Interpretación de y(t)
4. Recomendación para verificar el resultado
""".strip()


def explain_with_ai(payload: dict) -> str:
    client = OpenAI()
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.4"),
        input=build_prompt(payload),
    )
    return response.output_text.strip()
