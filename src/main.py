# Define funções que iniciam recursos antes da API receber requisições e os liberam após o encerramento. 
# Neste projeto, cria o gerenciador de ciclo de vida usado pelo FastAPI.
from contextlib import asynccontextmanager

# Permite representar datas no formato ano-mês-dia.
from datetime import date

# Fornece tipos.
from typing import AsyncGenerator, List, Optional

# Define dependências, cria a aplicação e trata respostas HTTP.
from fastapi import Depends, FastAPI, HTTPException, Response, status

# Valida dados de entrada e configura os modelos enviados como resposta pela API.
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Importa a classe responsável pelas operações no banco de dados.
from .dao.usuario_dao import UsuarioDAO

# Importa a classe que representa a entidade usuário.
from .model.usuario import Usuario

# A classe UsuarioEntrada é filha de BaseModel.
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

"""
asynccontextmanager permite executar ações antes e depois do funcionamento da API:
1. Antes do comando yield: inicialização, como preparar recursos, criar a tabela usuário, etc.
2. Depois do comando yield: encerramento e liberação desses recursos, como fechamento de conexões, etc.
No projeto, ele é aplicado ao gerenciador lifespan, que cria a tabela usuario antes da API começar a 
atender requisições.
Ele funciona assim:
1. Antes de yield: cria a tabela usuario.
2. yield: mantém a API em funcionamento e recebe requisições.
3. Depois de yield: executa alguma operação de finalização. Neste projeto, o programa
   imprime "Fim." quando a API é encerrada.
O asynccontextmanager transforma essa função em um gerenciador assíncrono usado pelo FastAPI no 
início e no fim da execução da aplicação.

No método lifespan, o underline (_) é um padrão usado apenas como nome convencional para 
um parâmetro que não será utilizado. O FastAPI exige que o gerenciador lifespan receba a 
instância da aplicação. Como esta função não usa essa instância, o nome "_" deixa a intenção clara.
Tecnicamente, "_" é apenas um nome de variável válido em Python, não uma palavra especial. 
Por convenção, ela indica que o valor pode ser ignorado. Se preferir um nome mais explícito,
você poderia usar algo como:

async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]: ...

Um AsyncGenerator é um gerador assíncrono: ele produz uma sequência de valores ao longo do 
tempo e pode pausar enquanto aguarda operações assíncronas. 

Exemplo:

async def numeros() -> AsyncGenerator[int, None]:
    yield 1
    yield 2

Os dois parâmetros do tipo têm significados diferentes:

AsyncGenerator[TipoProduzido, TipoEnviado]

1. TipoProduzido: o valor produzido pelo yield.
2. TipoEnviado: o valor que pode ser recebido ao executar yield novamente.

Exemplo:

async def exemplo() -> AsyncGenerator[str, int]:
    valor = yield "Primeiro"
    print(valor)


gerador = exemplo()
print(await anext(gerador))  # "Primeiro"

await gerador.asend(10)      # atribui 10 a "valor" e imprime 10

Nesse exemplo, "Primeiro" é produzido por yield. Um consumidor poderia usar asend() 
para enviar um inteiro de volta:

await gerador.asend(10)

Após esse asend(), a execução continua até yield ou até o gerador terminar.

Nesse caso, 10 é apenas um dado enviado pelo código que consome o gerador. 
asend() raramente é necessário.
yield é usado aqui principalmente para pausar o gerador e trocar valores quando 
esse recurso é relevante. 
Quando o gerador está pausado em yield, apenas o código original atribui o valor 
enviado por asend() à variável à esquerda de yield.

No projeto:

async def lifespan(...) -> AsyncGenerator[None, None]:

1. O primeiro None: yield não produz nenhum valor.
2. O segundo None: nenhum valor é enviado de volta ao gerador.
3. O yield serve principalmente para pausar o gerador e indicar ao FastAPI que a API iniciou e está pronta para receber requisições.

AsyncGenerator[None, None] é o tipo usado para indicar o que a função assíncrona lifespan 
retorna durante a execução:

1. AsyncGenerator: gerador assíncrono que usa async for ou yield em uma função assíncrona.
2. Primeiro None: tipo do valor emitido pelo yield. Como o yield está sozinho, não entrega nenhum valor.
3. Segundo None: tipo do valor recebido pelo código que envia dados ao gerador, não é usado no projeto.
Neste projeto, lifespan produz apenas o ciclo de vida da API, portanto o tipo é AsyncGenerator[None, None]. 
O None não indica que a função seja None; ele descreve os tipos associados ao yield.
"""
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    # Garante que a tabela exista antes de a API começar a receber requisições.
    obter_usuario_dao().create_table()
    yield
    print("\n\n --- Fim. --- \n\n")


# FastAPI gera a documentação interativa automaticamente em /docs (Swagger UI).
app = FastAPI(
    title="API de Usuários",
    description="CRUD com FastAPI, DAO e SQLite.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/usuarios", response_model = UsuarioResposta, status_code = status.HTTP_201_CREATED, summary = "Cadastrar usuário")
def criar_usuario(dados: UsuarioEntrada, dao: UsuarioDAO = Depends(obter_usuario_dao)) -> Usuario:
    # A API valida os dados; o DAO cuida exclusivamente da persistência.
    usuario = Usuario(nome=dados.nome, nascimento=dados.nascimento.isoformat() if dados.nascimento else None)
    return dao.create(usuario)


@app.get("/usuarios", response_model = List[UsuarioResposta], summary="Listar usuários")
def listar_usuarios(dao: UsuarioDAO = Depends(obter_usuario_dao)) -> List[Usuario]:
    return dao.read_all()


@app.get("/usuarios/{usuario_id}", response_model = UsuarioResposta, summary="Consultar usuário por ID")
def consultar_usuario(usuario_id: int, dao: UsuarioDAO = Depends(obter_usuario_dao)) -> Usuario:
    usuario = dao.read(usuario_id)
    if usuario is None:
        # HTTP 404 informa que o identificador solicitado não existe.
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Usuário não encontrado.")
    return usuario


@app.put("/usuarios/{usuario_id}", response_model = UsuarioResposta, summary = "Atualizar usuário")
def atualizar_usuario(usuario_id: int, dados: UsuarioEntrada, dao: UsuarioDAO = Depends(obter_usuario_dao)) -> Usuario:
    usuario = Usuario(id = usuario_id, nome = dados.nome, nascimento = dados.nascimento.isoformat() if dados.nascimento else None)
    if not dao.update(usuario):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Usuário não encontrado.")
    return usuario


@app.delete("/usuarios/{usuario_id}", status_code = status.HTTP_204_NO_CONTENT, response_class = Response, summary = "Excluir usuário")
def excluir_usuario(usuario_id: int, dao: UsuarioDAO = Depends(obter_usuario_dao)) -> Response:
    if not dao.delete(usuario_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Usuário não encontrado.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
