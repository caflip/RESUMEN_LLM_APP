"""
Extracción con LLM (Gemini) desde PDF/imagen/texto
--------------------------------------------
Lee un archivo (PDF o imagen) o un texto plano, lo envía al modelo de Google Gemini y exige que
responda EXCLUSIVAMENTE un resumen de 5 viñetas (bullets) en un json estructurado.

Variables de entorno necesarias
- GOOGLE_API_KEY: clave de API para Google GenAI.
- GENAI_MODEL  (opcional): nombre del modelo. Por defecto: gemini-2.5-flash.
"""
import json
import mimetypes
import os
from pathlib import Path
from google import genai
from google.genai import types


# Prompt por defecto: obliga al modelo a responder solo JSON y guía los campos comunes
DEFAULT_PROMPT = (
    "Eres un asistente de IA que resume documentos de forma concisa y estructurada.\n\n"
    "Instrucciones:\n"
    "- Lee el contenido proporcionado y genera EXACTAMENTE 5 viñetas resumen.\n"
    "- Cada viñeta debe tener máximo 20 palabras y estar en español neutro.\n"
    "- Responde ÚNICAMENTE con un JSON válido, sin texto adicional, sin código, sin comentarios, sin explicaciones.\n"
    "- No uses Markdown ni texto fuera del JSON.\n\n"
    "Formato de salida obligatorio:\n"
    '{\"summary_bullets\": [\"bullet1\", \"bullet2\", \"bullet3\", \"bullet4\", \"bullet5\"]}'
)


def _guess_mime(path):
    """Intenta deducir el tipo MIME del archivo por extensión; asume PDF si no puede."""
    mime, _ = mimetypes.guess_type(path.as_posix())
    return mime or "application/pdf"


def _load_client(model):
    """"
        Carga el clinete de Google GenAI usando variables de entorno y devuelve el modelo a usar

        -GOOGLE_API_KEY: clave de API para Google GenAI.
        -GENAI_MODEL  (opcional): nombre del modelo. Por defecto: gemini-2.5-flash.
    """
    api_key = os.getenv("GOOGLE_APY_KEY")
    if not api_key:
        raise ValueError("La variable de entorno GOOGLE_API_KEY no está definida.")

    model_name = model or os.getenv("GENAI_MODEL") or "gemini-2.5-flash"
    client = genai.Client(api_key=api_key)
    return client, model_name



def summarize_pdf_with_gemini(file_path, model):
    """
        Procesa un archivo con Gemini y devuelve un dict con la extracción.

        Parámetros:
        - file_path: ruta del archivo PDF/imagen a procesar.
        - model: nombre del modelo (por defecto se lee de `GENAI_MODEL`).

        Retorna:
        { ok: bool, data?: dict, model?: str, error?: str }
    """
    path = Path(file_path)
    if not path.exists():
        return {"ok": False, "error": f"Archivo no encontrado: {file_path}"}
    try:
        # Cliente Google GenAI
        client, use_model = _load_client(model=model)

        # Forzamos JSON puro en la salida
        gen_cfg = types.GenerateContentConfig(
            temperature=0.2,
            top_p=0.9,
            response_mime_type="application/json",
        )

        #Archivo como parte binaria con su tipo MIME
        file_bytes = path.read_bytes()
        part = types.Part.from_bytes(data=file_bytes, mime_type=_guess_mime(path))

        #Enviar archivo + prompt por defecto)
        resp = client.models.generate_content(
            model=use_model,
            contents=[part, DEFAULT_PROMPT],
            config=gen_cfg,
        )

        #Parseo seguro del JSON devuelto como texto
        text = (resp.text or "").strip()
        data = json.loads(text) if text else {}
        if not isinstance(data, dict):
            return {"ok": False, "error": "La respuesta del modelo no es un objeto JSON"}
        return {"ok": True, "data": data, "model": use_model}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    
def summarize_text_with_gemini(text, model):
    """
        Procesa texto plano con Gemini y devuelve un dict con la extracción.

        Útil cuando el contenido no proviene de un archivo sino de un textarea o fuente externa.

        Parámetros:
        - text: contenido textual a resumir.
        - model: nombre del modelo (por defecto se lee de `GENAI_MODEL`).

        Retorna:
        { ok: bool, data?: dict, model?: str, error?: str }
    """
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "No se proporciono texto para procesar"}
    try:
        # Cliente Google GenAI
        client, use_model = _load_client(model=model)

        # Forzamos JSON puro en la salida
        gen_cfg = types.GenerateContentConfig(
            temperature=0.2,
            top_p=0.9,
            response_mime_type="application/json",
        )

        
        part = types.Part.from_text(text=text)

        #Enviar archivo + prompt por defecto)
        resp = client.models.generate_content(
            model=use_model,
            contents=[part, DEFAULT_PROMPT],
            config=gen_cfg,
        )

        #Parseo seguro del JSON devuelto como texto
        text_raw = (resp.text or "").strip()
        data = json.loads(text_raw) if text_raw else {}
        if not isinstance(data, dict):
            return {"ok": False, "error": "La respuesta del modelo no es un objeto JSON"}
        return {"ok": True, "data": data, "model": use_model}
    except Exception as e:
        return {"ok": False, "error": str(e)}