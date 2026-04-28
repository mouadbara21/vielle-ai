import json
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def classify_document(embedding: list[float], db) -> str:
    """Classify the document to a thematic using pgvector similarity if thematics have centroids."""
    if not embedding or embedding[0] == 0.0:
        return "Non classifié"
        
    try:
        # Expected thematics might not have direct embeddings, so we might just 
        # mock classification if no centroid concept exists. Or try nearest document.
        # This is a simplified classifier for the MVP: assign based on most similar existing processed document's thematic.
        
        result = db.execute(
            text("""
                SELECT t.name, d.embedding <-> :embedding::vector AS distance
                FROM documents d
                JOIN sources s ON d.source_id = s.id
                JOIN folders f ON s.folder_id = f.id
                JOIN partitions p ON f.partition_id = p.id
                JOIN thematics t ON p.thematic_id = t.id
                WHERE d.embedding IS NOT NULL
                ORDER BY d.embedding <-> :embedding::vector LIMIT 1
            """), 
            {"embedding": json.dumps(embedding)}
        )
        match = result.fetchone()
        
        # If distance < 0.5 we consider it confident classification
        if match and match[1] < 0.5:
            return match[0]
            
        return "Général"
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return "Non classifié"
