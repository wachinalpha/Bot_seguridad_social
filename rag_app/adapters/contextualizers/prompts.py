from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

import yaml

from rag_app.config.settings import settings
from rag_app.domain.models import LawDocument


@lru_cache(maxsize=1)
def load_prompt_config() -> dict[str, Any]:
    prompt_path = settings.prompt_config_path_resolved
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt config not found: {prompt_path}")

    loaded = yaml.safe_load(prompt_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Prompt config must be a YAML mapping: {prompt_path}")
    return loaded


def _bullet_lines(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values)


def _section(title: str, values: list[str]) -> str:
    return f"{title}:\n{_bullet_lines(values)}"


def get_system_prompt() -> str:
    config = load_prompt_config()
    identity = config["identity"]
    instructions = config["instructions"]
    scope = instructions["scope"]
    output_rules = instructions["output_rules"]
    no_reasoning = output_rules["no_internal_reasoning"]

    parts = [
        f"ROL: {identity['role']}",
        _section("EXPERTISE", identity["expertise"]),
        f"TONO: {identity['tone']}",
        f"OBJETIVO: {instructions['objective']}",
        "REGLA DE ALCANCE (SCOPE):\n"
        f"- Alcance permitido: {scope['allowed']}\n"
        f"- Si la consulta está fuera de alcance, responde únicamente: \"{scope['out_of_scope_response']}\"",
        _section("REGLAS DE FUENTES (GROUNDING)", instructions["grounding_rules"]),
        _section("EVIDENCIA OBLIGATORIA", instructions["evidence_rules"]),
        _section("REGLAS DE INTERPRETACION", instructions["interpretation_rules"]),
        "FORMATO DE SALIDA:\n"
        f"- Siempre responde en {output_rules['language']}.\n"
        f"- Tu salida debe comenzar exactamente con: {output_rules['must_start_with']}\n"
        f"{_bullet_lines(output_rules['sections'])}",
        _section("SEGURIDAD", instructions["safety_rules"]),
    ]

    if no_reasoning.get("enabled"):
        parts.append(_section("PROHIBIDO MOSTRAR RAZONAMIENTO INTERNO", no_reasoning["rules"]))

    return "\n\n".join(parts)


def get_task_prompt_template() -> str:
    return load_prompt_config()["task_prompt"]["template"]


SYSTEM_PROMPT = get_system_prompt()


def build_task_prompt(query: str, law_docs: Sequence[LawDocument]) -> tuple[str, int, str]:
    context_parts = []

    for law_doc in law_docs:
        if not law_doc.file_path or not Path(law_doc.file_path).exists():
            continue

        text = Path(law_doc.file_path).read_text(encoding="utf-8")
        titulo = law_doc.titulo
        url = law_doc.url or "URL no disponible"
        context_parts.append(
            f"--- DOCUMENTO ---\n"
            f"TITULO: {titulo}\n"
            f"URL: {url}\n"
            f"CONTENIDO:\n{text}\n"
            f"--- FIN DOCUMENTO: {titulo} ---"
        )

    if not context_parts:
        raise ValueError("No valid law documents found to generate context")

    titles = ", ".join(d.titulo for d in law_docs)
    task_prompt = get_task_prompt_template().format(
        query=query,
        context_docs="\n\n".join(context_parts),
    )
    return task_prompt, len(context_parts), titles


def extract_final_answer(answer: str) -> str:
    """Remove provider reasoning preambles when the final formatted answer is present."""
    if not answer:
        return answer

    lower_answer = answer.lower()
    if "</think>" in lower_answer:
        end = lower_answer.rfind("</think>") + len("</think>")
        answer = answer[end:].lstrip()

    marker = "1) Respuesta:"
    marker_index = answer.find(marker)
    if marker_index > 0:
        return answer[marker_index:].strip()

    return answer.strip()
