# API CRUD de usuários com FastAPI, SQLite e DAO

* Este projeto demonstra uma API REST para cadastrar, consultar, atualizar e excluir usuários. 

* O padrão **Data Access Object (DAO)** mantém os comandos SQL
separados das rotas HTTP, e o SQLite persiste os dados em um arquivo local.

## Requisitos

- Python 3.9 ou superior
- Visual Studio Code
- Extensão [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) para executar o arquivo `teste.http`.

## Dependências

Na raiz do repositório, crie o arquivo `requirements.txt` com o conteúdo abaixo:

```text
# Carrega variáveis de ambiente a partir do arquivo .env:
python-dotenv>=1.0,<2.0
# Framework usado para criar a API REST e suas rotas HTTP:
fastapi>=0.110,<1.0
# Valida os dados de entrada e saída das requisições da API:
pydantic>=2.0,<3.0
# Servidor ASGI (Asynchronous Server Gateway Interface) responsável por executar a aplicação FastAPI:
uvicorn>=0.27,<1.0
```

## Ambiente virtual (virtual environment)

Um ambiente virtual (venv) é um ambiente Python isolado para um projeto. 

Ele mantém separadamente:

* Versões de pacotes.

* Dependências do projeto.

* O interpretador Python usado no projeto.

* Isso evita conflitos entre projetos que dependem de versões diferentes da mesma biblioteca.

Ao ativá-lo, o terminal passa a usar o Python e os pacotes daquele ambiente:

## Instalação

Ainda na raiz do repositório:

1. Crie um ambiente virtual (virtual environment):

```bash
python -m venv .venv
```

**OBS**:

No comando:

`python -m venv .venv`

1. **python**: executa o interpretador Python.
2. **-m**: significa `module`. Executa um módulo Python como script.
3. **venv**: nome do módulo padrão do Python que cria ambientes virtuais (virtual environment).
4. **.venv**: nome e caminho da pasta que será criada para conter o ambiente.

No caso, cria o ambiente na pasta `.venv` dentro do diretório atual. 

Você pode usar outro nome para a pasta, como `meuambiente`:

```bash
python -m venv meuambiente
```

Mas `.venv` é uma convenção comum e costuma ser ignorada pelo Git.

2. Ative o ambiente virtual (virtual environment):

```bash
source .venv/bin/activate # Linux/macOS.
```

**OBS**:

No Windows, ative o ambiente com:

```bash
.venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

ou

```bash
pip install --requirement requirements.txt
```

**OBS**:

No comando `pip install -r requirements.txt`, o `-r` significa `--requirement` (exigência, dependência).

Ele informa ao pip que as dependências devem ser lidas do arquivo indicado:

## Configuração com `.env`

O arquivo `.env` na raiz guarda configurações locais. 

A variável `SQLITE_DB_PATH` define o arquivo SQLite usado pela aplicação:

```env
SQLITE_DB_PATH=./banco_de_dados.db
```

O `python-dotenv` carrega o arquivo `.env`, e a `ConnectionFactory` usa a variável `SQLITE_DB_PATH` ao abrir conexões. 

Uma variável `SQLITE_DB_PATH` já definida no sistema tem
prioridade sobre o valor do `.env`. 

Caminhos relativos são resolvidos a partir do diretório em que o comando é executado. 

Sem essa configuração, o padrão é `teste.db`.

## Executar a API

Com o ambiente virtual ativado, inicie o servidor na raiz do projeto:

```bash
python -m uvicorn src.main:app --reload
```

Ao iniciar, a API cria a tabela `usuario` caso ainda não exista. 

## Swagger

A documentação Swagger fica disponível em:

<http://127.0.0.1:8000/docs>

A documentação alternativa fica disponível em:

<http://127.0.0.1:8000/redoc>.

## Rotas e códigos HTTP

| Método | Rota | Operação |
| --- | --- | --- |
| `POST` | `/usuarios` | Cadastra um usuário |
| `GET` | `/usuarios` | Lista os usuários |
| `GET` | `/usuarios/{usuario_id}` | Consulta um usuário pelo ID |
| `PUT` | `/usuarios/{usuario_id}` | Atualiza nome e nascimento |
| `DELETE` | `/usuarios/{usuario_id}` | Exclui um usuário |

O campo `nome` é obrigatório e limitado a 256 caracteres. Espaços no início e no fim são removidos, e nomes vazios ou compostos somente por espaços são rejeitados. 

O campo `nascimento` é opcional e usa o formato `AAAA-MM-DD`. 

Exemplo de corpo de requisição HTTP para criar ou atualizar:

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

1. Consultas e atualizações bem-sucedidas retornam `200 OK`; 
2. Uma exclusão bem-sucedida retorna `204 No Content`. 
3. Se o ID não existir, as rotas de consulta, atualização e exclusão retornam `404 Not Found`. 
5. Dados inválidos retornam `422 Unprocessable Entity`.

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

---

## Exercício

Em Python com FastAPI, escreva um algoritmo que:

1. Cadastre veículos no banco de dados SQLite, segundo o padrão "Data Access Object" (DAO). A classe Veiculo deve possuir as propriedades: marca, modelo, número do chassi, placa e cor. Após cadastrar todos os veículos, o algoritmo deve permitir:
  - Consultar os veículos cadastrados.
  - Atualizar os veículos cadastrados.
  - Excluir os veículos cadastrados.

2. Implemente o CRUD (Create, Read, Update, Delete) do banco de dados de uma padaria, empregando o padrão "Data Access Object" (DAO). Considere as tabelas:
  - Cliente(id_cliente, nome),
  - Pedido(id_pedido, id_cliente, data_pedido, total),
  - Produto(id_produto, nome, preco) e
  - ItemPedido(id_pedido, id_produto, quantidade).

3. Implemente o CRUD (Create, Read, Update, Delete) do banco de dados de uma agência de viagens, empregando o padrão "Data Access Object" (DAO). Considere as tabelas:
  - Cliente(id_cliente, nome),
  - Reserva(id_reserva, id_cliente, id_destino, data_viagem, valor) e
  - Destino(id_destino, nome_destino, pais).

4. Implemente o CRUD (Create, Read, Update, Delete) do banco de dados de uma clínica médica, empregando o padrão "Data Access Object" (DAO). Considere as tabelas:
  - Paciente(id_paciente, nome, telefone, email),
  - Medico(id_medico, nome, telefone, email, especialidade) e
  - Consulta(id_consulta, id_paciente, id_medico, data_consulta, valor).

5. Implemente o CRUD (Create, Read, Update, Delete) do banco de dados de uma farmácia, empregando o padrão "Data Access Object" (DAO). Considere as tabelas:
  - Medicamento(id_medicamento, nome, preco, data_validade),
  - Fornecedor(id_fornecedor, nome, telefone, email, endereco, cidade, estado) e
  - Compra(id_compra, id_medicamento, id_fornecedor, quantidade, data_compra).