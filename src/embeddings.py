from sentence_transformers import SentenceTransformer
import numpy as np

# Global variable to store the model
_model = None

def get_embeddings_model():
    """
    Load and return the sentence-transformers model.
    Uses a global variable to avoid reloading the model for each request.
    """
    global _model
    if _model is None:
        print("Loading embeddings model...")
        # all-MiniLM-L6-v2 is a good balance between performance and quality
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Embeddings model loaded successfully")
    return _model

def get_embeddings(text: str, model=None):
    """
    Generate embeddings for a text using the sentence-transformers model.
    """
    if model is None:
        model = get_embeddings_model()
    
    # Generate embedding
    embedding = model.encode(text)
    
    # Convert to list for storage in pgvector
    return embedding.tolist()
