# Permite acessar variáveis de ambiente do sistema.
import os

# Disponibiliza o módulo padrão para trabalhar com SQLite.
import sqlite3

# Representa caminhos de arquivos de forma independente do sistema operacional.
from pathlib import Path

# Permite declarar tipos opcionais e aceitar mais de um tipo.
from typing import Optional, Union

# Carrega variáveis definidas no arquivo .env.
from dotenv import load_dotenv


# Lê as variáveis do arquivo .env; variáveis já definidas no sistema têm prioridade.
load_dotenv()


class ConnectionFactory:
    """Centraliza a configuração e a criação das conexões SQLite."""

    """
    Optional[Union[str, Path]]: é uma anotação de tipo para o parâmetro ou 
                                atributo database_path:

    1. str: aceita uma string, como "banco.db".
    2. Path: aceita um objeto pathlib.Path, como Path("banco.db").
    3. Union[str, Path]: combina os dois tipos, permitindo uma string ou um Path.
    3. Optional[...]: permite também o valor None (nulo), indicando que nenhum 
                      caminho foi informado.
    Em resumo:
    database_path: Optional[Union[str, Path]]

    significa:
    database_path pode ser str, Path ou None (nulo).

    Exemplos válidos:
    1. database_path = "banco.db"
    2. database_path = Path("banco.db")
    3. database_path = None
    """
    def __init__(self, database_path: Optional[Union[str, Path]] = None) -> None:
        # Um caminho passado diretamente prevalece sobre a variável de ambiente.
        # Sem ambos, mantém ./bd/teste.db como padrão para compatibilidade.
        self.database_path = (database_path if database_path is not None else os.getenv("SQLITE_DB_PATH", "./bd/teste.db"))

    def create_connection(self) -> sqlite3.Connection:
        # sqlite3.connect abre o banco existente ou cria o arquivo se necessário.
        return sqlite3.connect(self.database_path)
