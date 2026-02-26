# from src.config import CHUNK_OVERLAP_CHARS, CHUNK_SIZE_CHARS
import hashlib

CHUNK_SIZE_CHARS = 800
CHUNK_OVERLAP_CHARS = 120

def split_text_into_chunks(text: str, chunk_size: int, chunk_overlap: int) -> list[dict]:
    """
        Goal: split one string deterministically into overlapping chunks
        Input: text, size of chunk, overlap size of chunk
        Output: List of Dicts: [{chunk_index, char_start, char_end,text}]
        Notes: 
        - Check arguments -> loop to split chunks
        - returns [] for empty/whitespace, raises ValueError for invalid params
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be < chunk_size")
    
    if not isinstance(text,str):
        raise ValueError('Text must be string')

    if not text or not text.strip(): 
        return []

    text_length = len(text)
    chunks = []
    chunk_index = 0
    start= 0
    stride = chunk_size - chunk_overlap
    while start < text_length:
        end = min(start+chunk_size, text_length)
        chunks.append({"chunk_index": chunk_index,
                    "char_start": start, 
                    "char_end": end, 
                    "text": text[start:end]})
        if end == text_length: 
            break
        start = start + stride
        chunk_index += 1
    return chunks

def build_chunk_records_from_document(document: dict) -> list[dict]:
    """
        Goal: Convert one normalized document into storage-ready chunk records
        Input: one normalized document dict
        Output: List of chunk record dicts. Each record contains: 
            [chunk_id, document_ref, content_hash, metadata, timestamps, is_deleted]
        Notes: 
        - document -> labeled chunks -> return labeled chunks
        - raises ValueError for missing id/source, does not write to MongoDB
    """
    if not isinstance(document, dict): 
        raise ValueError('Document must be dict type')
    
    records = []
    document_id = document_id = str(document.get("id", "")).strip()
    if not document_id:
        raise ValueError("document.id is required to build chunk records")
    
    metadata = document.get('metadata', {})
    if not isinstance(metadata, dict):
        raise ValueError("document.metadata must be a dict")
    
    source = metadata.get('source', '')
    if not source:
        raise ValueError("document.metadata.source is required to build chunk records")

    document_content = document.get('text', '')
    document_type = document.get('type', '')
    chunks = split_text_into_chunks(document_content, CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS)
    source_updated_at = document.get('updated_at', '')
    for chunk in chunks:
        chunk_index = chunk.get('chunk_index', 0)
        chunk_id = f'{source}:' + f'{document_id}:' + f'{chunk_index}'
        document_ref = {"source": source, "id": document_id}        
        char_start = chunk.get('char_start', 0)
        char_end = chunk.get('char_end', 0)
        text = chunk.get('text', '')
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        is_deleted = False
        record = {'chunk_id': chunk_id,
                  'document_ref': document_ref,
                  'type': document_type,
                  'chunk_index': chunk_index,
                  'char_start': char_start,
                  'char_end': char_end,
                  'text': text,
                  'content_hash': content_hash,
                  'metadata': metadata,
                  'source_updated_at': source_updated_at,
                  'updated_at': None,
                  'is_deleted': is_deleted}
        records.append(record)
    return records

if __name__ == "__main__":
    doc = {
        "id": "abc123",
        "type": "article",
        "text": "abcdefghij" * 5,
        "updated_at": "2026-02-26T10:00:00Z",
        "metadata": {"source": "notion", "title": "Test Note"},
    }
    records = build_chunk_records_from_document(doc)
    print(len(records))
    print(records[0])




