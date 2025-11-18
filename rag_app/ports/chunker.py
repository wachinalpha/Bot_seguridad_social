from typing import Protocol, List, Dict
from rag_app.domain.models import Chunk , Law   

class ChunkerPort(Protocol):
    
    def chunk_law(self,law:Law) -> List[Chunk]:
        ...

    def contextualize_chunk(self, chunk_text: str, full_document: str, law_metadata: Dict[str, str]) -> Dict[str, str]:
        ... 

