from langdetect import detect, DetectorFactory

# Set seed for deterministic results
DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """Detect language of the given text."""
    try:
        if not text.strip():
            return "unknown"
        return detect(text)
    except Exception:
        return "unknown"
