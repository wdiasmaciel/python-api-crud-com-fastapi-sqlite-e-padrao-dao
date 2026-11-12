from .model.usuario import Usuario
from .dao.usuario_dao import UsuarioDAO


def main() -> None:
    # O DAO concentra o acesso ao banco; o programa usa seus métodos sem
    # precisar conhecer os comandos SQL executados internamente.
    usuario_dao = UsuarioDAO()
    usuario_dao.create_table()

    # CREATE: cadastra o usuário e guarda no objeto o ID gerado pelo SQLite.
    usuario = Usuario(nome = "Ana", nascimento = "2000-06-07")
    usuario = usuario_dao.create(usuario)

    # READ: consulta pelo ID e exibe os dados encontrados.
    usuario_dao.read(usuario.id)

    # UPDATE: altera o objeto e persiste a mudança no banco.
    usuario.nome = "Ana Silva"
    usuario_dao.update(usuario)
    usuario_dao.read(usuario.id)

    # DELETE: remove o registro; a consulta seguinte demonstra que ele não existe mais.
    usuario_dao.delete(usuario)
    usuario_dao.read(usuario.id)

    # Repete o fluxo de cadastro e atualização com outros usuários.
    usuario = Usuario(nome = "Bruna", nascimento = "2006-08-07")
    usuario = usuario_dao.create(usuario)
    usuario_dao.read(usuario.id)

    usuario.nome = "Bruna Gomes"
    usuario_dao.update(usuario)
    usuario_dao.read(usuario.id)

    usuario = Usuario(nome = "Carlos", nascimento = "2009-11-15")
    usuario = usuario_dao.create(usuario)
    usuario_dao.read(usuario.id)

    usuario.nome = "Carlos Pereira"
    usuario_dao.update(usuario)
    usuario_dao.read(usuario.id)


# Executa o exemplo apenas quando este módulo é iniciado diretamente.
if __name__ == "__main__":
    main()
