from docling.document_converter import DocumentConverter, InputFormat
from docling.chunking import HybridChunker
from pathlib import Path
from rag_app.ports.chunker import ChunkerPort
from rag_app.domain.models import Chunk, Law
from typing import Protocol, List, Dict, Optional
import json

class Hybrid_chunker(ChunkerPort):

    Converter = DocumentConverter()
 
    def __init__(self):
        pass    

    """ESTE MÉTODO NO ES PARTE DEL PROTOCOLO, ES SOLO DE UTILIDAD PARA TESTEO
    LO PODEMOS SACAR DESPUÉS"""
    def converter_document_md(self, url: str):
        result = self.Converter.convert(url).document
        result_md = result.export_to_markdown()
        return result_md
    
    def chunk_law(self, law: Law, tokenizer="sentence-transformers/all-MiniLM-L6-v2", max_tokens = 500) -> List[Chunk]:
        result = self.Converter.convert(law.url).document
        chunker = HybridChunker(
            heading_as_metadata=False,  # Los headings se incluyen en el chunk
            tokenizer= tokenizer, # que tokenizer usar
            max_tokens= max_tokens # Máximo tokens por chunk
        )

        chunks = list(chunker.chunk(dl_doc=result))

        chunk_con_metadata = [] 
        for i,chunk in enumerate(chunks):
            chunk_completos = Chunk(
                id=f"ley_{law.numero}_chunk_{i}",
                text=chunk.text,
                contextualized_text=None,
                metadata={
                    'ley_numero': law.numero,
                    'ley_nombre': law.nombre,
                    'ley_url': law.url,
                    'ley_año': law.año
                },
                law=law
            )
            chunk_con_metadata.append(chunk_completos)
        return chunk_con_metadata







def main():
    path_json = Path("./rag_app/config/leyes_config.json")

    # Leer el archivo y cargarlo como diccionario
    with path_json.open("r", encoding="utf-8") as f:
        data = json.load(f)
    ley=data["leyes"][0]
    # Tomar la primera ley

    print(ley)
    ley_1 = Law(**ley)

    chunker = Hybrid_chunker()
    chunks = chunker.chunk_law(ley_1)
    for i, chunk in enumerate(chunks):
        print(f"\n🔹 Chunk {i}")
        print("Texto:", chunk.text)
        print("Metadata:", "ley numero:", chunk.metadata["ley_numero"], "nombre de ley:", chunk.metadata["ley_nombre"], "año:", chunk.metadata["ley_año"])


if __name__ == "__main__":
    main()