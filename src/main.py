from contextlib import asynccontextmanager
from datetime import date
from typing import AsyncGenerator, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .dao.usuario_dao import UsuarioDAO
from .model.usuario import Usuario


class UsuarioEntrada(BaseModel):
    """Define e valida os dados enviados para criar ou atualizar um usuário."""

    nome: str = Field(min_length=1, max_length=256)
    nascimento: Optional[date] = None

    @field_validator("nome")
    @classmethod
    def remover_espacos_do_nome(cls, nome: str) -> str:
        # Impede nomes vazios ou compostos somente por espaços.
        nome = nome.strip()
        if not nome:
            raise ValueError("O nome não pode ficar vazio.")
        return nome


class UsuarioResposta(BaseModel):
    """Descreve os campos de usuário que a API devolve nas respostas."""

    # Permite criar a resposta diretamente a partir do dataclass Usuario.
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    nascimento: Optional[date] = None


def obter_usuario_dao() -> UsuarioDAO:
    # O DAO usa a ConnectionFactory, responsável por ler a configuração do .env.
    return UsuarioDAO()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    # Garante que a tabela exista antes de a API começar a receber requisições.
    obter_usuario_dao().create_table()
    yield


# FastAPI gera a documentação interativa automaticamente em /docs (Swagger UI).
app = FastAPI(
    title="API de Usuários",
    description="Exemplo didático de CRUD com FastAPI, DAO e SQLite.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post(
    "/usuarios",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar usuário",
)
def criar_usuario(
    dados: UsuarioEntrada,
    dao: UsuarioDAO = Depends(obter_usuario_dao),
) -> Usuario:
    # A API valida os dados; o DAO cuida exclusivamente da persistência.
    usuario = Usuario(
        nome=dados.nome,
        nascimento=dados.nascimento.isoformat() if dados.nascimento else None,
    )
    return dao.create(usuario)


@app.get(
    "/usuarios",
    response_model=List[UsuarioResposta],
    summary="Listar usuários",
)
def listar_usuarios(
    dao: UsuarioDAO = Depends(obter_usuario_dao),
) -> List[Usuario]:
    return dao.read_all()


@app.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioResposta,
    summary="Consultar usuário por ID",
)
def consultar_usuario(
    usuario_id: int,
    dao: UsuarioDAO = Depends(obter_usuario_dao),
) -> Usuario:
    usuario = dao.read(usuario_id)
    if usuario is None:
        # HTTP 404 informa que o identificador solicitado não existe.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )
    return usuario


@app.put(
    "/usuarios/{usuario_id}",
    response_model=UsuarioResposta,
    summary="Atualizar usuário",
)
def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioEntrada,
    dao: UsuarioDAO = Depends(obter_usuario_dao),
) -> Usuario:
    usuario = Usuario(
        id=usuario_id,
        nome=dados.nome,
        nascimento=dados.nascimento.isoformat() if dados.nascimento else None,
    )
    if not dao.update(usuario):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )
    return usuario


@app.delete(
    "/usuarios/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Excluir usuário",
)
def excluir_usuario(
    usuario_id: int,
    dao: UsuarioDAO = Depends(obter_usuario_dao),
) -> Response:
    if not dao.delete(usuario_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
