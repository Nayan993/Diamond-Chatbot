import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer

VECTOR_DIM = 384

class Retriever:
    def __init__(self, vector_dir=None, model_name="all-MiniLM-L6-v2"):
        # Default vector_dir relative to backend folder
        if vector_dir is None:
            vector_dir = os.path.join(os.path.dirname(__file__), "vectorstore")
        
        self.model = SentenceTransformer(model_name)
        self.vector_dir = vector_dir
        self.index = None
        self.chunks = []
        self.load_index()

    def load_index(self):
        idx_path = os.path.join(self.vector_dir, "lore_index.faiss")
        meta_path = os.path.join(self.vector_dir, "lore_metadata.pkl")

        if not os.path.exists(idx_path) or not os.path.exists(meta_path):
            raise FileNotFoundError(
                f"Vectorstore not found at {self.vector_dir}. "
                f"Please build it first using embeddings.py"
            )

        # Load FAISS index
        self.index = faiss.read_index(idx_path)

        # Load metadata chunks
        with open(meta_path, "rb") as f:
            self.chunks = pickle.load(f)

    def retrieve(self, query, top_k=3):
        """
        Retrieve top_k relevant text chunks for a given query.
        """
        query_vector = self.model.encode([query])
        D, I = self.index.search(query_vector, top_k)
        results = [self.chunks[i] for i in I[0]]
        return results
