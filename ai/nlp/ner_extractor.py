import spacy
import logging

logger = logging.getLogger(__name__)

# Load models lazily to avoid loading at startup if not used
_nlp_fr = None
_nlp_en = None

def get_model(lang: str):
    global _nlp_fr, _nlp_en
    try:
        if lang == 'fr':
            if _nlp_fr is None:
                _nlp_fr = spacy.load('fr_core_news_md')
            return _nlp_fr
        else:
            # Fallback to english or minimal model
            if _nlp_en is None:
                import spacy.cli
                try:
                    _nlp_en = spacy.load('en_core_web_sm')
                except OSError:
                    spacy.cli.download('en_core_web_sm')
                    _nlp_en = spacy.load('en_core_web_sm')
            return _nlp_en
    except Exception as e:
        logger.error(f"Failed to load spaCy model for {lang}: {e}")
        return None

def extract_entities(text: str, language: str) -> dict:
    """Extract Named Entities (Persons, Orgs, Locations) using spaCy."""
    nlp = get_model(language)
    entities = {"persons": [], "organizations": [], "locations": []}
    
    if not nlp or not text:
        return entities
        
    # Process mostly the first part of text for speed if too long
    doc = nlp(text[:100000])
    
    for ent in doc.ents:
        if ent.label_ == 'PER' or ent.label_ == 'PERSON':
            if ent.text not in entities["persons"]:
                entities["persons"].append(ent.text)
        elif ent.label_ == 'ORG':
            if ent.text not in entities["organizations"]:
                entities["organizations"].append(ent.text)
        elif ent.label_ == 'LOC' or ent.label_ == 'GPE':
            if ent.text not in entities["locations"]:
                entities["locations"].append(ent.text)
                
    return entities
