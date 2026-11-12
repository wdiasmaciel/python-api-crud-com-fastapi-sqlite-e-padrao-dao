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
        # closing fecha a conexão ao sair do bloco; with connection confirma
        # a transação se não houver erro (ou faz rollback caso haja exceção).
        with closing(self.connection_factory.create_connection()) as connection:
            with connection:
                connection.execute(create_table_sql)
        print("Tabela 'usuario' criada ou já existe!")

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

        print(
            "USUÁRIO GRAVADO NO BANCO DE DADOS:"
            f"\nID: {usuario.id}"
            f"\nNOME: {usuario.nome}"
            f"\nDATA DE NASCIMENTO: {usuario.nascimento}"
        )
        return usuario

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
            print("Usuário não encontrado!")
            return None

        # Converte a linha retornada pelo banco em um objeto do domínio.
        usuario = Usuario(
            id=row["id"],
            nome=row["nome"],
            nascimento=row["nascimento"],
        )
        print(
            "USUÁRIO LIDO DO BANCO DE DADOS:"
            f"\nID: {usuario.id}"
            f"\nNOME: {usuario.nome}"
            f"\nDATA DE NASCIMENTO: {usuario.nascimento}"
        )
        return usuario

    def update(self, usuario: Usuario) -> None:
        # Atualiza os dados cujo ID coincide com o do objeto recebido.
        update_sql = (
            "UPDATE usuario SET nome = ?, nascimento = ? WHERE id = ?"
        )
        with closing(self.connection_factory.create_connection()) as connection:
            with connection:
                connection.execute(
                    update_sql,
                    (usuario.nome, usuario.nascimento, usuario.id),
                )
        print(f"O usuário {usuario.nome} foi atualizado no banco de dados!")

    def delete(self, usuario: Usuario) -> None:
        # Remove o registro usando o ID, sem depender do nome do usuário.
        delete_sql = "DELETE FROM usuario WHERE id = ?"
        with closing(self.connection_factory.create_connection()) as connection:
            with connection:
                connection.execute(delete_sql, (usuario.id,))
        print(f"O usuario {usuario.nome} foi removido do BD.")
