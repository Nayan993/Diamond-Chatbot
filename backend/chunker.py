import os

def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into chunks of `chunk_size` words with `overlap`.
    Returns list of text chunks.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap  # overlap for context
    return chunks

def load_lorebook(path=None):
    # Use default path relative to backend folder
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "../lorebook/raw_lore.txt")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Lorebook not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return text
