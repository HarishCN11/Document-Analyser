import os
import json

# Folder to save vector data
VECTOR_DIR = "data/knowledge_base/vectors"
os.makedirs(VECTOR_DIR, exist_ok=True)

def create_chunks(text, filename, chunk_size=500):
    """
    Splits the text into chunks of roughly `chunk_size` words.
    Returns a list of dictionaries: [{'id': str, 'text': str}]
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk_text = " ".join(words[i:i+chunk_size])
        chunk_id = f"{filename}_chunk_{i//chunk_size}"
        chunks.append({"id": chunk_id, "text": chunk_text})
    return chunks

def store_embeddings(chunks):
    """
    Placeholder for storing embeddings.
    Currently, it just saves the chunks to a JSON file.
    """
    file_path = os.path.join(VECTOR_DIR, "chunks.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"[vector_store] Stored {len(chunks)} chunks to {file_path}")
