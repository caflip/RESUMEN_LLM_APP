import json
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
import tempfile

# Cargar variables de entorno desde el archivo .env
load_dotenv()
from utils.gemini_summarize import summarize_pdf_with_gemini, summarize_text_with_gemini





st.title("Resumen de Documentos con Google Gemini")
st.write("Sube un archivo PDF o ingresa texto para obtener un resumen utilizando Google Gemini.")

# Opción para subir archivo PDF
opcion1, opcion2 = st.tabs(["Resumen desde PDF", "Resumen desde Texto"])

with opcion1:
    uploaded_file = st.file_uploader("Sube un archivo (PDF/imagen)",
                                    type=["pdf", "png", "jpg", "jpeg"])
    
    model = os.getenv("GENAI_MODEL") or "gemini-2.5-flash"

    if st.button("Generar Resumen desde PDF o imagen", use_container_width=True, type="primary"):
        if not uploaded_file:
            st.error("Por favor selecciona un archivo.")
        else:
            # Guardar el archivo subido en un archivo temporal seguro
            ext = "." + uploaded_file.name.split(".")[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = Path(tmp.name)


            with st.spinner("Procesando con Gemini…"):
                res = summarize_pdf_with_gemini(str(tmp_path), model=model)

            if res.get("ok"):
                data = res["data"]
                st.success(f"Modelo: {res.get('model')}")
                st.subheader("JSON")
                st.code(json.dumps(data, ensure_ascii=False, indent=2), language="json")

                # Vista amigable de las viñetas
                bullets = data.get("summary_bullets", [])
                if isinstance(bullets, list):
                    st.subheader("Vista")
                    for i, b in enumerate(bullets, 1):
                        st.write(f"- {b}")
            else:
                st.error(res.get("error", "Error desconocido."))

with opcion2:
    text = st.text_area("Pega texto aquí", height=240, placeholder="Pega o escribe el contenido a resumir…")
    model = os.getenv("GENAI_MODEL") or "gemini-2.5-flash"
    if st.button("Resumir texto", use_container_width=True, type="primary", key="btn_text"):
        if not text.strip():
            st.error("Por favor ingresa texto.")
        else:
            with st.spinner("Procesando con Gemini…"):
                res = summarize_text_with_gemini(text, model=model)

            if res.get("ok"):
                data = res["data"]
                st.success(f"Modelo: {res.get('model')}")
                st.subheader("JSON")
                st.code(json.dumps(data, ensure_ascii=False, indent=2), language="json")

                bullets = data.get("summary_bullets", [])
                if isinstance(bullets, list):
                    st.subheader("Vista")
                    for i, b in enumerate(bullets, 1):
                        st.write(f"- {b}")
            else:
                st.error(res.get("error", "Error desconocido."))