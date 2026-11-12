import os
import sqlite3
from pathlib import Path
from typing import Optional, Union

from dotenv import load_dotenv


# Lê as variáveis do arquivo .env; variáveis já definidas no sistema têm prioridade.
load_dotenv()


class ConnectionFactory:
    """Centraliza a configuração e a criação das conexões SQLite."""

    def __init__(
        self, database_path: Optional[Union[str, Path]] = None
    ) -> None:
        # Um caminho passado diretamente prevalece sobre a variável de ambiente.
        # Sem ambos, mantém teste.db como padrão para compatibilidade.
        self.database_path = (
            database_path
            if database_path is not None
            else os.getenv("SQLITE_DB_PATH", "teste.db")
        )

    def create_connection(self) -> sqlite3.Connection:
        # sqlite3.connect abre o banco existente ou cria o arquivo se necessário.
        return sqlite3.connect(self.database_path)
