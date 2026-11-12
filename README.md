# API CRUD de usuários com FastAPI, SQLite e DAO

Este projeto demonstra uma API REST para cadastrar, consultar, atualizar
e excluir usuários. O padrão **Data Access Object (DAO)** mantém os comandos SQL
separados das rotas HTTP, e o SQLite persiste os dados em um arquivo local.

## Requisitos

- Python 3.9 ou superior
- Visual Studio Code
- Extensão [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) para executar `teste.http`

## Instalação

Na raiz do repositório, crie e ative um ambiente virtual e instale as dependências:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows, ative o ambiente com `.venv\Scripts\activate`.

## Configuração com `.env`

O arquivo `.env` na raiz guarda configurações locais. A variável
`SQLITE_DB_PATH` define o arquivo SQLite usado pela aplicação:

```env
SQLITE_DB_PATH=./banco_de_dados.db
```

O `python-dotenv` carrega o arquivo, e a `ConnectionFactory` usa a variável ao
abrir conexões. Uma variável `SQLITE_DB_PATH` já definida no sistema tem
prioridade sobre o valor do `.env`. Caminhos relativos são resolvidos a partir
do diretório em que o comando é executado. Sem essa configuração, o padrão é
`teste.db`.

O `.env` está no `.gitignore` para não versionar configurações locais. Ao clonar
o projeto, crie esse arquivo na raiz usando o bloco acima como exemplo.

## Executar a API

Com o ambiente virtual ativado, inicie o servidor na raiz do projeto:

```bash
python -m uvicorn src.main:app --reload
```

Ao iniciar, a API cria a tabela `usuario` caso ainda não exista. A documentação
Swagger fica disponível em <http://127.0.0.1:8000/docs> e a documentação
alternativa em <http://127.0.0.1:8000/redoc>.

## Rotas e códigos HTTP

| Método | Rota | Operação |
| --- | --- | --- |
| `POST` | `/usuarios` | Cadastra um usuário |
| `GET` | `/usuarios` | Lista os usuários |
| `GET` | `/usuarios/{usuario_id}` | Consulta um usuário pelo ID |
| `PUT` | `/usuarios/{usuario_id}` | Atualiza nome e nascimento |
| `DELETE` | `/usuarios/{usuario_id}` | Exclui um usuário |

O campo `nome` é obrigatório e limitado a 256 caracteres. Espaços no início e no
fim são removidos, e nomes vazios ou compostos somente por espaços são
rejeitados. `nascimento` é opcional e usa o formato `AAAA-MM-DD`. Exemplo de
corpo para criar ou atualizar:

```json
{
  "nome": "Ana Silva",
  "nascimento": "2000-06-07"
}
```

O cadastro retorna `201 Created` e inclui o ID atribuído pelo SQLite:

```json
{
  "id": 1,
  "nome": "Ana Silva",
  "nascimento": "2000-06-07"
}
```

Consultas e atualizações bem-sucedidas retornam `200 OK`; uma exclusão
bem-sucedida retorna `204 No Content`. Se o ID não existir, as rotas de consulta,
atualização e exclusão retornam `404 Not Found`. Dados inválidos retornam
`422 Unprocessable Entity`.

## Testar com REST Client

1. Inicie o servidor.
2. Abra [`teste.http`](./teste.http) no VS Code.
3. Clique em **Send Request** acima de cada requisição. Para consultar, atualizar
   ou excluir um usuário, substitua o `1` da URL pelo ID devolvido pela
   requisição de cadastro.

## Como o padrão DAO aparece neste projeto

- `src/main.py` define os modelos de entrada e saída, valida os dados e atende às
  requisições HTTP. As rotas não executam comandos SQL.
- `src/model/usuario.py` representa a entidade `Usuario` usada entre as camadas.
- `src/dao/usuario_dao.py` cria a tabela e executa as operações SQL de criação,
  leitura, atualização e exclusão.
- `src/database/connection_factory.py` carrega a configuração do ambiente e
  centraliza a criação das conexões SQLite.

Assim, a rota traduz HTTP em chamadas ao DAO, e o DAO traduz essas chamadas em
operações no banco. Os valores SQL são passados por parâmetros (`?`), em vez de
serem concatenados ao comando.
