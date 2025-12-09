# Diamond Bot - README

Diamond Bot is a Retrieval-Augmented Generation (RAG) backend that uses a local lorebook with FAISS vectorstore and sentence-transformers to retrieve relevant context, then forwards queries with context to an LLM (e.g., Gemini) to generate grounded answers.

## Project Structure

```
backend/
├── main.py                # FastAPI app (endpoints: /health, /ask)
├── retriever.py           # Loads FAISS index + metadata; retrieves top-k chunks
├── embeddings.py          # Build vectorstore: load lorebook → chunk → embed → save
├── chunker.py             # load_lorebook(), chunk_text()
├── llm.py                 # Wrapper to call Gemini/LLM: ask_gemini()
├── vectorstore/           # Created by embeddings.py
│   ├── lore_index.faiss
│   └── lore_metadata.pkl
└── lorebook/
    └── raw_lore.txt       # Source knowledge file (your lorebook)
```

## Prerequisites

- Python 3.9+
- pip
- Virtual environment (recommended)
- GPU optional (CPU works but slower for embedding generation)
- Internet access for package downloads and LLM API calls

## Installation

### 1. Create and activate virtual environment

```bash
# Linux / macOS
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install fastapi uvicorn sentence-transformers faiss-cpu pydantic

# Add your LLM client library (example for Gemini):
pip install google-generative-ai
```

**Required Python libraries:**
- fastapi
- uvicorn
- faiss-cpu (or faiss-gpu for GPU support)
- sentence-transformers
- pydantic
- pickle (built-in)
- Your LLM library (e.g., google-generative-ai or openai)

## Setup

### Step 1: Prepare Lorebook

Place your knowledge file at:
```
backend/lorebook/raw_lore.txt
```

This should be a plain text file containing all the reference content you want Diamond Bot to use.

### Step 2: Build the Vectorstore

Run this **once** (or when lorebook changes):

```bash
# From backend/ directory
python -c "from embeddings import create_embeddings_model, build_vectorstore; m=create_embeddings_model(); build_vectorstore(m)"
```

Or using Python REPL:
```python
from embeddings import create_embeddings_model, build_vectorstore
model = create_embeddings_model("all-MiniLM-L6-v2")
build_vectorstore(model, lorebook_path=None, vector_dir="vectorstore")
```

This creates:
- `backend/vectorstore/lore_index.faiss`
- `backend/vectorstore/lore_metadata.pkl`

**Notes:**
- Default chunk size: 500 words with 50-word overlap (configurable in chunker.py)
- Default model: `all-MiniLM-L6-v2` → 384-dim vectors
- If you change the model, ensure VECTOR_DIM matches the model's embedding size

### Step 3: Configure API Keys

Store API keys securely in environment variables:

```bash
export LLM_API_KEY="your_api_key_here"
```

**Never hardcode API keys in your code!**

### Step 4: Start the Backend Server

```bash
# From backend/ directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
```bash
GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok"
}
```

### Ask Question
```bash
POST http://localhost:8000/ask
Content-Type: application/json

{
  "question": "What is Diamond Bot?"
}
```

**Response:**
```json
{
  "answer": "..."
}
```

### Example cURL Request

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Diamond Bot?"}'
```

## How It Works

1. **Preprocessing** (`embeddings.py`): Chunks `raw_lore.txt` into ~500-word pieces, encodes each with SentenceTransformer, and stores vectors in FAISS with metadata in pickle file.

2. **Server Startup** (`main.py`): Loads Retriever which reads FAISS index and metadata.

3. **Query Processing** (on POST /ask):
   - Validates incoming question
   - Converts question to embedding using SentenceTransformer
   - Performs FAISS search for top-k (default: 3) nearest chunks
   - Calls `ask_gemini(question, chunks)` to generate answer using retrieved context
   - Returns JSON response with the answer

4. **LLM Integration** (`llm.py`): Formats prompt with system instructions, retrieved context, and question; calls LLM API; returns final answer.

## CORS Configuration

By default, `main.py` allows requests from `http://localhost:3000`. Update `allow_origins` if your frontend runs elsewhere.

## File Responsibilities

| File | Purpose |
|------|---------|
| `main.py` | FastAPI server and endpoints |
| `retriever.py` | Load FAISS + metadata; handle retrieval requests |
| `embeddings.py` | Build vectorstore (chunk → embed → index) |
| `chunker.py` | Load lorebook and chunk text |
| `llm.py` | Wrap LLM API calls (Gemini or other) |
| `raw_lore.txt` | Knowledge source |

## Troubleshooting

### FileNotFoundError: Vectorstore not found
→ Run `embeddings.py` to build the vectorstore first.

### ModuleNotFoundError: faiss
→ Install `faiss-cpu` or `faiss-gpu` appropriately.

### Model mismatch (VECTOR_DIM)
→ Update VECTOR_DIM to match your sentence-transformer model's embedding size.

### Slow embedding generation
→ Use batch processing, GPU acceleration, or a faster embedding model. For large lorebooks, process in chunks and monitor memory.

### CORS issues
→ Adjust `allow_origins` in `main.py`.

## Tuning & Optimization

- **Chunk Size**: Reduce for more granular retrieval (increases vectorstore size)
- **top_k**: Increase to provide more context to the LLM
- **Metadata**: Add chunk metadata (title/source/page) for LLM citation capabilities
- **FAISS Optimization**: Use vector quantization or IVF for very large vectorstores

## Quick Viva Statements

**English (30s):**
"This project implements a Retrieval-Augmented Generation pipeline. We preprocess the lorebook into overlapping chunks, create vector embeddings with SentenceTransformer, store them in a FAISS index, and at runtime retrieve the top-k chunks for a query. The retrieved chunks plus the user's question are sent to an LLM via ask_gemini() to produce grounded answers. The backend is a FastAPI app exposing /ask and /health."

**Hinglish (30s):**
"Yeh project RAG pipeline use karta hai. Pehle lorebook ko chunks me todte hain, har chunk ka embedding banate hain aur FAISS me store karte hain. Runtime pe user ka question aane par retriever top-k relevant chunks lata hai. Yeh chunks aur question LLM ko diye jate hain ask_gemini() se aur grounded answer return hota hai. Backend FastAPI se /ask aur /health endpoints provide karta hai."

## Useful Commands

```bash
# Create environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Build vectorstore
python -c "from embeddings import create_embeddings_model, build_vectorstore; m=create_embeddings_model(); build_vectorstore(m)"

# Run backend
uvicorn main:app --reload --port 8000
```

## Suggested .gitignore

```
/vectorstore/
*.pyc
__pycache__/
.env
.venv/
*.pkl
*.faiss
```

## Frontend Setup

The Diamond Bot frontend is built with Create React App.

### Project Structure

```
frontend/
├── src/
│   ├── App.js           # Main application component
│   ├── components/      # React components
│   └── index.js         # Entry point
├── public/
└── package.json
```

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Available Scripts

#### `npm start`
Runs the app in development mode. Open [http://localhost:3000](http://localhost:3000) to view it in your browser. The page will reload when you make changes. You may also see any lint errors in the console.

#### `npm test`
Launches the test runner in interactive watch mode. See the [running tests documentation](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

#### `npm run build`
Builds the app for production to the `build` folder. It correctly bundles React in production mode and optimizes the build for the best performance. The build is minified and the filenames include the hashes. Your app is ready to be deployed!

See the [deployment documentation](https://facebook.github.io/create-react-app/docs/deployment) for more information.

#### `npm run eject`
**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project and copy all configuration files and transitive dependencies (webpack, Babel, ESLint, etc) into your project for full control.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature.

### Connecting Frontend to Backend

Ensure your backend is running on `http://localhost:8000` before starting the frontend. The frontend makes API calls to:
- `GET http://localhost:8000/health` - Check backend status
- `POST http://localhost:8000/ask` - Submit questions

Update the API endpoint in your frontend code if your backend runs on a different port.

### Running Both Frontend and Backend

```bash
# Terminal 1 - Backend
cd backend
source .venv/bin/activate  # Activate virtual environment
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm start
```

### Learn More

- [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started)
- [React documentation](https://reactjs.org/)
- [Code Splitting](https://facebook.github.io/create-react-app/docs/code-splitting)
- [Analyzing Bundle Size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)
- [Making a Progressive Web App](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)
- [Advanced Configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Troubleshooting Frontend

**Port already in use:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9  # macOS/Linux
# Or change port
PORT=3001 npm start
```

**Build fails to minify:**
See [troubleshooting documentation](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)

**CORS errors:**
Ensure backend's `main.py` includes your frontend URL in `allow_origins`

## Security Best Practices

- Store API keys in environment variables only
- Do not commit vectorstore files to version control
- Implement rate limiting for production deployments
- Use HTTPS in production
- Validate and sanitize all user inputs
