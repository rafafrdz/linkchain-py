from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.docstore.document import Document as LangChainDocument
import os

from database import get_db_session
from embeddings import get_embeddings, get_embeddings_model

# Database connection string for LangChain
CONNECTION_STRING = f"postgresql://{os.getenv('POSTGRES_USER', 'user')}:{os.getenv('POSTGRES_PASSWORD', 'password')}@{os.getenv('POSTGRES_HOST', 'db')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'vectordb')}"

# Table name for LangChain
COLLECTION_NAME = "documents"

def get_langchain_embeddings():
    """
    Create a LangChain embeddings object using the HuggingFaceEmbeddings wrapper
    """
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def semantic_search(query: str, limit: int = 3):
    """
    Perform semantic search using LangChain and pgvector
    """
    # Get embeddings for the query
    embeddings_model = get_embeddings_model()
    query_embedding = get_embeddings(query, embeddings_model)

    # Use SQLAlchemy directly for more control
    session = get_db_session()
    try:
        # Execute a vector similarity search
        from database import Document
        from sqlalchemy import text

        # Using cosine similarity
        stmt = text(f"""
            SELECT id, content, 1 - (embedding <=> (:query_embedding)::vector) as similarity
            FROM documents
            ORDER BY embedding <=> (:query_embedding)::vector
            LIMIT :limit
        """)

        result = session.execute(stmt, {
            "query_embedding": query_embedding,
            "limit": limit
        })

        # Format results
        results = []
        for row in result:
            results.append({
                "id": row[0],
                "content": row[1],
                "similarity": float(row[2])
            })

        return results
    finally:
        session.close()
