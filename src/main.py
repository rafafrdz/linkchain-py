from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os

from database import init_db, get_db_session
from embeddings import get_embeddings_model, get_embeddings
from search import semantic_search

# Initialize FastAPI app
app = FastAPI(title="Semantic Search API")

# Models for request/response
class DocumentRequest(BaseModel):
    texts: List[str]

class DocumentResponse(BaseModel):
    document_ids: List[int]

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    results: List[Dict[str, Any]]

@app.on_event("startup")
async def startup_event():
    # Initialize database
    init_db()
    # Load embeddings model
    get_embeddings_model()

@app.post("/documents", response_model=DocumentResponse)
async def add_documents(request: DocumentRequest):
    """
    Add documents to the knowledge base.
    Each document will be converted to embeddings and stored in the database.
    """
    if not request.texts or len(request.texts) == 0:
        raise HTTPException(status_code=400, detail="No texts provided")
    
    try:
        # Get embeddings for each text
        embeddings_model = get_embeddings_model()
        document_ids = []
        
        # Get database session
        session = get_db_session()
        
        for text in request.texts:
            # Generate embedding
            embedding = get_embeddings(text, embeddings_model)
            
            # Store document and embedding in database
            from database import Document
            doc = Document(content=text, embedding=embedding)
            session.add(doc)
            session.flush()
            document_ids.append(doc.id)
        
        session.commit()
        return DocumentResponse(document_ids=document_ids)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding documents: {str(e)}")
    finally:
        session.close()

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the knowledge base with a natural language question.
    Returns the most relevant documents.
    """
    if not request.question:
        raise HTTPException(status_code=400, detail="No question provided")
    
    try:
        # Perform semantic search
        results = semantic_search(request.question, limit=3)
        return QueryResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying documents: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
