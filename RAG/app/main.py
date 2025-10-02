# app/main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from app.models import QueryRequest, QueryResponse, RetrievedDocument,Message
from app.rag import rag_system, initialize_rag_system
import uvicorn
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG System API",
    description="API for a Retrieval-Augmented Generation system using FastAPI",
    version="1.0.0"
)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your React app's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
@app.on_event("startup")
async def startup_event():
    """
    Initialize the RAG system when the application starts.
    """
    logger.info("Initializing RAG system...")
    # Run the initialization in a separate thread to avoid blocking
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, initialize_rag_system)
    logger.info("RAG system initialized successfully.")

@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """
    Endpoint to handle queries for the RAG system.

    - **query**: The input query string.
    - **top_k**: (Optional) Number of top documents to retrieve.
    """
    try:
        logger.info(f"Received query: '{request.query}' with top_k: {request.top_k}")

        # Call rag_system and unpack the results
        answer, doc_score_pairs = rag_system(
            request.query, 
            top_k=request.top_k,
            memory=request.memory
        )

        # Log the retrieved doc_score_pairs for debugging
        logger.debug(f"doc_score_pairs: {doc_score_pairs}")
        sorted_doc_score_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)
        # Ensure doc_score_pairs is a list of tuples
        if not isinstance(doc_score_pairs, list) or not all(isinstance(pair, tuple) and len(pair) == 2 for pair in doc_score_pairs):
            logger.error("Invalid data structure for doc_score_pairs.")
            raise ValueError("Invalid data structure for doc_score_pairs.")

        # Process documents
        retrieved_documents = []
        for idx, (doc, score) in enumerate(doc_score_pairs, start=1):
            # Clean up content if necessary
            cleaned_content = doc.replace('## English Translation:', '').strip()
            logger.debug(f"Processed Document {idx}: {cleaned_content}")

            # Append document to the response
            retrieved_documents.append(RetrievedDocument(header="", content=cleaned_content))

        # Return the response
        return QueryResponse(
            answer=answer,
            retrieved_documents=retrieved_documents
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Optionally, include a root endpoint
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the RAG System API. Use /docs for API documentation."}

# Entry point for running the app with `python main.py`
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
