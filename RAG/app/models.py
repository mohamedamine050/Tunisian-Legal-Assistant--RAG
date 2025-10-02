# app/models.py

from pydantic import BaseModel,Field
from typing import List

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    memory: List[Message] = Field(default_factory=list, description="Last 10 messages from conversation history")

class RetrievedDocument(BaseModel):
    header: str=""
    content: str

class QueryResponse(BaseModel):
    answer: str
    retrieved_documents: List[RetrievedDocument]
