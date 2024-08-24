
# E-commerce com Flask

Este é um projeto simples de e-commerce desenvolvido com Flask, que inclui funcionalidades CRUD (adicionar, remover, alterar e listar) e um sistema de login. O objetivo é fornecer uma base para um e-commerce funcional, com uma interface básica e operações essenciais.
Funcionalidades

## Funcionalidades

- Página Inicial: Tela de login para acessar o painel de administração.
- CRUD de Produtos: Interface para gerenciar produtos:
    - Adicionar Produto
    - Listar Produtos
    - Editar Produto
    - Excluir Produto
- Sistema de Login: Controle de acesso às funcionalidades de gerenciamento de produtos.


## Instalação

Instale my-project com npm
### 1- Clone o repositório
```bash
  git clone https://github.com/usuario/ecommerce-flask.git
  cd ecommerce-flask

```
### 2- Crie um ambiente virtual

    
```bash
  python -m venv venv
```

### 3- Ative o ambiente virtual
- Windows
```bash
  venv\Scripts\activate

```
- Linux/macOS
```bash
  source venv/bin/activate

```

### 4- Instale as dependências
```bash
  pip install -r requirements.txt

```

### 5- Execute o aplicativo
```bash
  python app.py

```

O aplicativo estará disponível em http://localhost:5000.
## Uso/Exemplos

### 1 - Acesse a Página Inicial

- Faça login com as credenciais padrão (ou adicione um usuário via código).

### 2 - Gerencie Produtos

- Após o login, use a interface para adicionar, listar, editar e excluir produtos.

## Dependências

- Flask
- Flask-Login
- Flask-WTF
- Flask-Bootstrap (opcional para estilização)
- Flask-SQLAlchemy (para gerenciamento de banco de dados)
## Suporte

Para suporte, mande um email para harthopfpereira96@gmail.com ou entre em nosso canal do Slack.

