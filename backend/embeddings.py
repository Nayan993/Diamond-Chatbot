import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from chunker import load_lorebook, chunk_text

VECTOR_DIM = 384  # depends on the model

def create_embeddings_model(model_name="all-MiniLM-L6-v2"):
    """
    Initialize the sentence transformer model.
    """
    return SentenceTransformer(model_name)

def build_vectorstore(model, lorebook_path=None, vector_dir="vectorstore"):
    """
    Build FAISS vectorstore from the lorebook text.
    """
    os.makedirs(vector_dir, exist_ok=True)

    # Load lorebook
    text = load_lorebook(lorebook_path)
    chunks = chunk_text(text)

    # Create embeddings
    vectors = model.encode(chunks, show_progress_bar=True)

    # FAISS index
    index = faiss.IndexFlatL2(VECTOR_DIM)
    index.add(vectors)

    # Save index and metadata
    faiss.write_index(index, os.path.join(vector_dir, "lore_index.faiss"))
    with open(os.path.join(vector_dir, "lore_metadata.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    print(f"Vectorstore built with {len(chunks)} chunks.")
