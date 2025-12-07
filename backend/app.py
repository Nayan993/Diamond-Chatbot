from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from retriever import Retriever
from llm import ask_gemini

app = FastAPI(title="Diamond Bot API")

# Allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for request
class QuestionRequest(BaseModel):
    question: str

# Initialize retriever once
try:
    retriever = Retriever()
except FileNotFoundError as e:
    retriever = None
    print(f"Warning: {e}. Build vectorstore first using embeddings.py")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask_question(req: QuestionRequest):
    if not retriever:
        raise HTTPException(status_code=500, detail="Vectorstore not found. Build it first using embeddings.py")

    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Retrieve relevant chunks from lorebook
    try:
        chunks = retriever.retrieve(question, top_k=3)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving context: {str(e)}")

    # Ask Gemini LLM
    try:
        answer = ask_gemini(question, chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Gemini API: {str(e)}")

    return {"answer": answer}
