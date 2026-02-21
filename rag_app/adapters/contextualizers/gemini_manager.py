from google import genai
from google.genai import types
from pathlib import Path
import json
import logging
import re
from typing import Sequence

from rag_app.domain.models import LawDocument
from rag_app.config.settings import settings

logger = logging.getLogger(__name__)

_LEYES_CONFIG = Path(__file__).resolve().parents[2] / "config" / "leyes_config.json"


# ============================================================================
# System Prompt (fijo, se envía como system_instruction)
# ============================================================================
SYSTEM_PROMPT = """\
Eres un asistente legal especializado EXCLUSIVAMENTE en Seguridad Social de Argentina (ANSES, asignaciones familiares, AUH, prestaciones, regímenes vinculados).

REGLA DE ALCANCE (SCOPE):
- Solo puedes responder consultas relacionadas con seguridad social / ANSES.
- Si la consulta NO está relacionada, responde únicamente:
  "Solo puedo responder consultas de Seguridad Social (ANSES)."

REGLAS DE FUENTES (GROUNDING):
- Debes usar ÚNICAMENTE la información del bloque CONTEXTO provisto por el sistema (leyes/documentos).
- NO uses conocimiento general, memoria, ni información externa.
- NO inventes artículos, requisitos, definiciones, fechas, montos, procedimientos o excepciones.

EVIDENCIA OBLIGATORIA:
- Cada afirmación factual debe estar respaldada por evidencia textual del CONTEXTO.
- Debes citar SIEMPRE la fuente con el formato exacto: [DOC_ID:Lx-Ly] (donde DOC_ID es el identificador del documento y Lx-Ly son las líneas aproximadas).
- Si no existe evidencia suficiente en el CONTEXTO, responde:
  "No surge de los documentos provistos."
  y (opcional) pide qué documento/dato faltaría.

REGLAS DE INTERPRETACIÓN:
- Si hay ambigüedad (por ejemplo el caso del usuario no especifica datos clave), indícalo y formula preguntas puntuales, pero NO supongas.
- Si hay conflicto entre documentos del CONTEXTO, indícalo explícitamente con citas y NO elijas arbitrariamente; explica ambas lecturas.
- No combines reglas de distintos documentos como si fueran una sola norma. Si usas más de un documento, aclara qué aporta cada uno y cita ambos.

FORMATO DE SALIDA:
Siempre responde en español y con estas secciones:

1) Respuesta (conclusión breve)
2) Evidencia (citas): lista de fragmentos o referencias del CONTEXTO que sustentan la respuesta
3) Observaciones / Faltantes (si aplica): qué parte no está cubierta por el CONTEXTO o qué datos faltan para decidir

SEGURIDAD:
- No brindes asesoramiento legal definitivo; expresa que la respuesta es informativa y depende del texto provisto.
- No sugieras acciones fuera del CONTEXTO (por ejemplo trámites) si el CONTEXTO no los describe.
"""


# ============================================================================
# Task Prompt (template, se arma con cada request)
# ============================================================================
TASK_PROMPT = """\
CONSULTA DEL USUARIO:
{query}

INSTRUCCIONES DE RESPUESTA:
- Responde SOLO con el CONTEXTO. No uses conocimiento externo.
- Cita toda afirmación factual con el formato de cita del CONTEXTO.
- Si la consulta NO es de seguridad social / ANSES: responde exactamente "Solo puedo responder consultas de Seguridad Social (ANSES)."
- Si la respuesta no surge del CONTEXTO: responde "No surge de los documentos provistos."

CONTEXTO (hasta 3 documentos recuperados por similitud):
{context_docs}

FORMATO DE SALIDA (obligatorio):
1) Respuesta:
<respuesta breve y directa>

2) Evidencia (citas):
- <punto de evidencia 1> [DOC_ID:Lx-Ly]
- <punto de evidencia 2> [DOC_ID:Lx-Ly]
...

3) Observaciones / Faltantes (si aplica):
- <ambigüedad o dato faltante> [cita si aplica]
- <si no surge, indicar qué faltaría>
"""


class GeminiManager:
    """Adapter for generating answers using Gemini API."""
    
    def __init__(self, api_key: str = None):
        api_key = api_key or settings.gemini_api_key
        self.client = genai.Client(api_key=api_key)
        self.model_name = settings.llm_model
        self._url_map = self._build_url_map()
        logger.info(f"Initialized GeminiManager with model: {self.model_name}")

    @staticmethod
    def _build_url_map() -> dict:
        """
        Build a mapping from doc_id (ley_24714) → URL from leyes_config.json.
        Falls back gracefully if the file is missing.
        """
        try:
            with open(_LEYES_CONFIG, encoding="utf-8") as f:
                config = json.load(f)
            url_map = {}
            for ley in config.get("leyes", []):
                numero = ley.get("numero", "").strip()
                url = ley.get("url", "").strip()
                if numero and url:
                    doc_id = f"ley_{numero}"
                    url_map[doc_id] = url
            logger.info(f"Loaded {len(url_map)} law URLs from leyes_config.json")
            return url_map
        except Exception as e:
            logger.warning(f"Could not load leyes_config.json: {e}")
            return {}

    def _linkify_citations(self, text: str) -> str:
        """
        Replace inline citations like [ley_24714:L142-L147] with markdown links
        that point to the official law URL.

        Example:
            [ley_24714:L142-L147]  →  [ley_24714:L142-L147](https://...)
        """
        # Matches: [ley_XXXX:Lx-Ly] or [ley_XXXX:Lx]
        pattern = re.compile(r'\[(?P<citation>(ley_[\w\-]+):L[\d]+(?:-L[\d]+)?)\]')

        def replace(m: re.Match) -> str:
            citation = m.group("citation")
            doc_id = m.group(2)        # e.g. ley_24714
            url = self._url_map.get(doc_id)
            if url:
                return f"[{citation}]({url})"
            return m.group(0)          # no URL found, leave as-is

        return pattern.sub(replace, text)
    
    def generate_answer(self, query: str, law_docs: Sequence[LawDocument]) -> str:
        """
        Generate answer to a query using full law context from multiple documents.
        
        Args:
            query: User's question
            law_docs: List of law documents with file_path to markdown content
            
        Returns:
            Generated answer from the LLM
        """
        try:
            # Build context from all law documents
            context_parts = []
            
            for law_doc in law_docs:
                if not law_doc.file_path or not Path(law_doc.file_path).exists():
                    logger.warning(f"File path not found: {law_doc.file_path}, skipping")
                    continue
                
                text = Path(law_doc.file_path).read_text(encoding='utf-8')
                doc_id = law_doc.id
                titulo = law_doc.titulo
                context_parts.append(
                    f"--- DOCUMENTO: {titulo} (ID: {doc_id}) ---\n{text}\n--- FIN: {doc_id} ---"
                )
            
            if not context_parts:
                raise ValueError("No valid law documents found to generate context")
            
            context_docs = "\n\n".join(context_parts)
            
            # Build the task prompt with query and context
            task_prompt = TASK_PROMPT.format(
                query=query,
                context_docs=context_docs,
            )
            
            titles = ", ".join(d.titulo for d in law_docs)
            logger.info(f"Generating answer using {len(context_parts)} laws: {titles}")

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=task_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                ),
            )
            
            logger.info(f"Generated answer using {len(context_parts)} law(s)")
            return self._linkify_citations(response.text)
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
