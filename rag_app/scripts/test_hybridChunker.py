from rag_app.domain.models import Law
from rag_app.adapters.chunkers.hybrid_chunker import Hybrid_chunker
from pathlib import Path
import json

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