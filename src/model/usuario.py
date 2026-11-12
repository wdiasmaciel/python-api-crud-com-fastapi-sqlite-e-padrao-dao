from dataclasses import dataclass
from typing import Optional


@dataclass
class Usuario:
    # O SQLite preenche o ID ao cadastrar; antes disso, ele é None.
    id: Optional[int] = None
    # Valores padrão permitem criar o objeto sem informar todos os campos.
    nome: str = ""
    # A data é armazenada como texto no formato AAAA-MM-DD neste exemplo.
    nascimento: Optional[str] = None
