# Resumen 5 bullets (Gemini)

## Variables
- `GOOGLE_API_KEY` (obligatoria)
- `GENAI_MODEL` (opcional, por defecto `gemini-2.5-flash`)

## Local
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # poner tu API key
streamlit run app.py
