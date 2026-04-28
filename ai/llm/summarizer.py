import os
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)
    logger.info("Gemini API key configured.")
else:
    logger.warning("GEMINI_API_KEY is not set. LLM tasks will fail.")

# Use a default model, e.g., gemini-1.5-flash for summarization
model_name = "gemini-1.5-flash"


def generate_summary(title: str, content: str) -> str:
    """Generate a brief summary of the article."""
    if not api_key:
        return "Erreur: Clé API Gemini non configurée."
        
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"Résume cet article en français, en 3 à 5 phrases claires et concises. Mets en évidence les informations principales.\n\nTitre: {title}\nContenu: {content}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini summarization failed: {e}")
        return ""


def generate_watch_note(combined_text: str) -> str:
    """Generate a watch note from multiple documents."""
    if not api_key:
        return "Erreur: Clé API Gemini non configurée."

    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"Rédige une note de veille de qualité professionnelle en français basée sur les documents fournis ci-dessous. Extraits les tendances majeures, les enjeux clés et structure la note avec des listes à puces.\n\nDocuments:\n{combined_text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini watch note generation failed: {e}")
        return ""
