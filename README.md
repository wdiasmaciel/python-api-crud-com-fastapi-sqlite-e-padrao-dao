# Python + SQLite: exemplo de Data Access Object (DAO)

Este projeto demonstra o padrão DAO em Python com SQLite. 

O exemplo apresenta as operações CREATE, READ, UPDATE, DELETE (CRUD): criar a tabela, cadastrar, consultar, atualizar e remover um usuário.

## Configurar o banco de dados

O projeto lê o caminho do banco pela variável `SQLITE_DB_PATH`, definida no arquivo
`.env`. O arquivo `.env.example` serve como modelo; copie-o para `.env` e ajuste o
caminho se desejar. O arquivo `.env` é ignorado pelo Git.

Por exemplo:

```env
SQLITE_DB_PATH=./banco_de_dados.db
```

Caminhos relativos são interpretados a partir do diretório em que o programa é
executado. Se a variável não estiver definida, o programa usa `teste.db`.

## Requisitos

- Python 3.8 ou superior
- Dependência para carregar variáveis do arquivo `.env`:

```bash
pip install -r requirements.txt
```

O acesso ao SQLite usa a biblioteca padrão do Python (`sqlite3`).

## Executar

Na raiz do repositório, rode:

```bash
python -m src.main
```

O programa cria o arquivo de banco indicado por `SQLITE_DB_PATH` (ou `teste.db`
quando a variável não estiver definida), cria a tabela `usuario` e executa o fluxo
de cadastro, consulta, atualização e remoção de usuários.
