from tools.vector_store import create_chunks, store_embeddings
from tools.pdf_utils import extract_document_text


class KnowledgeService:
    def __init__(self):
        self.ready = False

    def ingest_document(self, uploaded_file):
        text = extract_document_text(uploaded_file)
        chunks = create_chunks(text, uploaded_file.name)
        store_embeddings(chunks)
        self.ready = True

    def ingest_pdf(self, pdf_file):
        self.ingest_document(pdf_file)

    def is_ready(self):
        return self.ready
