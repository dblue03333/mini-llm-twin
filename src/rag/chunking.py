# from src.config import CHUNK_OVERLAP_CHARS, CHUNK_SIZE_CHARS

CHUNK_SIZE_CHARS = 800
CHUNK_OVERLAP_CHARS = 120

def split_text_into_chunks(text: str, chunk_size: int, chunk_overlap: int) -> list[dict]:
    """
        Goal: split one string deterministically into overlapping chunks
        Input: text, size of chunk, overlap size of chunk
        Output: List of Dicts: [{chunk_index, char_start, char_end,text}]
        Notes: Check arguments -> loop to split chunks
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be < chunk_size")
    
    if not text or not text.strip(): 
        return []

    text_length = len(text)
    res = []
    chunk_index = 0
    start= 0
    stride = chunk_size - chunk_overlap
    while start < text_length:
        end = min(start+chunk_size, text_length)
        res.append({"chunk_index": chunk_index,
                    "char_start": start, 
                    "char_end": end, 
                    "text": text[start:end]})
        if end == text_length: break
        start = start + stride
        chunk_index += 1
    return res

def build_chunk_records_from_document(document: dict) -> list[dict]:
    """
        Goal: Convert one normalized document into storage-ready chunk records
        Input: one normalized document dict
        Output: List of chunk record dicts. Each record contains: 
            [chunk_id, document_ref, content_hash, metadata, timestamps, is_deleted]
        Notes: 
    """
    return []

if __name__ == "__main__":
    cases = [
        ("", 4, 1),
        ("hello", 10, 2),
        ("abcdefghij", 4, 1),
    ]

    for text, size, overlap in cases:
        print(f"\ntext={text!r}, size={size}, overlap={overlap}")
        print(split_text_into_chunks(text, size, overlap))




