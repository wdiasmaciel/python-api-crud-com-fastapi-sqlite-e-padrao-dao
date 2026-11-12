import sqlite3
from contextlib import closing
from typing import Optional

from ..database.connection_factory import ConnectionFactory
from ..model.usuario import Usuario


class UsuarioDAO:
    """Implementa as operações de persistência para a entidade Usuario."""

    def __init__(
        self, connection_factory: Optional[ConnectionFactory] = None
    ) -> None:
        # Permite injetar outra fábrica (útil em testes); se omitida, usa a padrão.
        self.connection_factory = connection_factory or ConnectionFactory()

    def create_table(self) -> None:
        # IF NOT EXISTS permite executar o exemplo mais de uma vez sem erro.
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(256) NOT NULL,
                nascimento TEXT
            )
        """
        # closing fecha a conexão; o bloco interno confirma a transação ou
        # desfaz as alterações se ocorrer uma exceção.
        with closing(self.connection_factory.create_connection()) as connection:
            with connection:
                connection.execute(create_table_sql)

    def create(self, usuario: Usuario) -> Usuario:
        # Os ? são parâmetros: os valores são enviados separados do SQL,
        # evitando montar a instrução com concatenação de texto.
        insert_sql = "INSERT INTO usuario (nome, nascimento) VALUES (?, ?)"
        with closing(self.connection_factory.create_connection()) as connection:
            with connection:
                cursor = connection.execute(
                    insert_sql, (usuario.nome, usuario.nascimento)
                )
                # lastrowid contém a chave primária atribuída pelo SQLite.
                usuario.id = cursor.lastrowid

        return usuario

    def read_all(self) -> list[Usuario]:
        # A ordenação por ID torna a listagem previsível para clientes da API.
        select_sql = "SELECT id, nome, nascimento FROM usuario ORDER BY id"
        with closing(self.connection_factory.create_connection()) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(select_sql).fetchall()

        # Cada linha do SQLite é convertida em um objeto do domínio.
        return [
            Usuario(
                id=row["id"],
                nome=row["nome"],
                nascimento=row["nascimento"],
            )
            for row in rows
        ]

    def read_last_inserted_id(self, connection: sqlite3.Connection) -> int:
        # MAX(id) obtém o maior identificador; uma tabela vazia não tem máximo.
        row = connection.execute(
            "SELECT MAX(id) AS max_id FROM usuario"
        ).fetchone()
        if row is None or row[0] is None:
            # -1 sinaliza que ainda não há registros.
            return -1
        return int(row[0])

    def read(self, usuario_id: int) -> Optional[Usuario]:
        # Busca somente o registro com o ID informado.
        select_sql = "SELECT id, nome, nascimento FROM usuario WHERE id = ?"
        with closing(self.connection_factory.create_connection()) as connection:
            # Com sqlite3.Row, as colunas podem ser acessadas pelo nome.
            connection.row_factory = sqlite3.Row
            row = connection.execute(select_sql, (usuario_id,)).fetchone()

        if row is None:
            # Optional[Usuario]: retorna None quando não há correspondência.
            return None

        # Converte a linha retornada pelo banco em um objeto do domínio.
        return Usuario(
            id=row["id"],
            nome=row["nome"],
            nascimento=row["nascimento"],
        )

    def update(self, usuario: Usuario) -> bool:
        # Atualiza o registro e informa se o ID existia no banco.
        update_sql = (
            "UPDATE usuario SET nome = ?, nascimento = ? WHERE id = ?"
        )
        with closing(self.connection_factory.create_connection()) as connection:
            with connection:
                cursor = connection.execute(
                    update_sql,
                    (usuario.nome, usuario.nascimento, usuario.id),
                )
                return cursor.rowcount > 0

    def delete(self, usuario_id: int) -> bool:
        # Remove o registro e informa se o ID existia no banco.
        delete_sql = "DELETE FROM usuario WHERE id = ?"
        with closing(self.connection_factory.create_connection()) as connection:
            with connection:
                cursor = connection.execute(delete_sql, (usuario_id,))
                return cursor.rowcount > 0
