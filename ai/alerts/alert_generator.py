import json
from sqlalchemy import text
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def check_and_generate_alerts(document_id: int, content: str, entities: dict, sentiment_score: float, db):
    """Evaluate keyword triggers against document content to generate alerts."""
    
    try:
        # Get document thematic mapping
        doc_info = db.execute(
            text("""
                SELECT t.id, d.title
                FROM documents d
                JOIN sources s ON d.source_id = s.id
                JOIN folders f ON s.folder_id = f.id
                JOIN partitions p ON f.partition_id = p.id
                JOIN thematics t ON p.thematic_id = t.id
                WHERE d.id = :id
            """), {"id": document_id}
        ).fetchone()
        
        if not doc_info:
            return
            
        thematic_id, title = doc_info[0], doc_info[1]
        
        # Create a new document alert
        db.execute(
            text("""
                INSERT INTO alerts (document_id, thematic_id, type, priority, title, description, ai_score, created_at) 
                VALUES (:doc_id, :them_id, 'new_document', 'medium', :title, :desc, 0.5, :now)
            """), {
                "doc_id": document_id, "them_id": thematic_id, 
                "title": f"Nouveau document: {title}", "desc": "Nouveau contenu détecté.",
                "now": datetime.utcnow()
            }
        )
        
        # Fetch triggers for this thematic
        triggers = db.execute(
            text("SELECT id, name, query_expression FROM keyword_triggers WHERE thematic_id = :thematic_id AND is_active = true"),
            {"thematic_id": thematic_id}
        ).fetchall()
        
        content_lower = content.lower() if content else ""
        
        for trigger in triggers:
            trigger_id, trigger_name, expr = trigger
            # Extremely simple parsing: just look for the expression as a substring
            # In a real app, you would parse AND/OR
            match_found = False
            
            expr_lower = expr.lower().strip()
            if "and" in expr_lower:
                parts = [p.strip() for p in expr_lower.split("and")]
                match_found = all(p in content_lower for p in parts)
            elif "or" in expr_lower:
                parts = [p.strip() for p in expr_lower.split("or")]
                match_found = any(p in content_lower for p in parts)
            else:
                match_found = expr_lower in content_lower
                
            if match_found:
                ai_score = 0.8 # high score for direct trigger match
                
                # Check entity impact (simple heuristic)
                if any(expr_lower in ent.lower() for ents in entities.values() for ent in ents):
                    ai_score = 0.95
                    
                priority = 'high' if ai_score > 0.8 else 'medium'
                
                db.execute(
                    text("""
                        INSERT INTO alerts (document_id, thematic_id, trigger_id, type, priority, title, description, ai_score, created_at) 
                        VALUES (:doc_id, :them_id, :trig_id, 'keyword_match', :prio, :title, :desc, :score, :now)
                    """), {
                        "doc_id": document_id, "them_id": thematic_id, "trig_id": trigger_id,
                        "prio": priority, "title": f"Mot-clé détecté: {trigger_name}",
                        "desc": f"L'expression de recherche '{expr}' a été détectée dans le document.",
                        "score": ai_score, "now": datetime.utcnow()
                    }
                )
        db.commit()
    except Exception as e:
        logger.error(f"Alert generation failed for doc {document_id}: {e}")
        db.rollback()
