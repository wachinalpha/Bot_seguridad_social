from dataclasses import dataclass
from typing import Optional, Dict, List
import numpy as np

@dataclass
class Law:
    numero: str
    nombre: str
    url: str
    año: Optional[int] = None
    categoria: Optional[str] = None



@dataclass
class Chunk:
    id: str
    text: str
    contextualized_text: Optional[str]
    metadata: dict
    law: Optional[Law]= None
    emedding: Optional[np.ndarray] = None


@dataclass
class QueryResult:
    chunk: Chunk
    score: float
    rank: int    