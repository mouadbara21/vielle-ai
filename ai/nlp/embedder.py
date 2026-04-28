from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# Lazy loading of model
_model = None

def get_embedder_model():
    global _model
    if _model is None:
        try:
            logger.info("Loading sentence-transformers model...")
            _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        except Exception as e:
            logger.error(f"Failed to load embedder model: {e}")
            _model = None
    return _model

def generate_embedding(text: str) -> list[float]:
    """Generate 384-dimensional vector for a text."""
    if not text:
        return [0.0] * 384
        
    model = get_embedder_model()
    if not model:
        # Fallback to zeros if model fails
        return [0.0] * 384
        
    # Truncate text to avoid memory issues (usually limit to 500-1000 words)
    truncated_text = text[:2000]
    
    embedding = model.encode(truncated_text)
    return embedding.tolist()
