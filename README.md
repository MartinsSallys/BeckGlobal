# BeckGlobal 🚀

Boilerplate para APIs modernas com FastAPI, PostgreSQL e Docker. Pronto para servir de base para novos projetos, com autenticação JWT, migrations e testes automatizados.

---

## ✨ Tecnologias

- Python 3.12+
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL 16
- Alembic (migrations)
- Poetry (gerenciamento de dependências)
- Docker & Docker Compose
- JWT Authentication (PyJWT + bcrypt)
- Pydantic Settings
- Pytest + Coverage
- Ruff (lint + format)
- MyPy (type check)
- Pre-commit
- Taskipy

---

## 📂 Estrutura

```text
app/
├── api/
│   ├── routes/        # health, auth e users
│   ├── dependencies.py # dependências (usuário autenticado)
│   ├── router.py      # registro dos routers
│   └── schemas.py     # schemas Pydantic
├── core/              # configuração, logging, exceções e segurança
├── database/          # engine, sessão e Base do SQLAlchemy
├── models/            # modelos SQLAlchemy
└── main.py            # entrypoint da aplicação

alembic/               # migrations
tests/                 # testes automatizados (SQLite in-memory)
```

---

## ⚡ Início rápido (com Docker)

Requer apenas Docker e Docker Compose instalados.

```bash
git clone https://github.com/MartinsSallys/BeckGlobal.git
cd BeckGlobal
cp .env.example .env
docker compose up -d --build
```

Pronto. A API estará em `http://localhost:8000`. As migrations são aplicadas
automaticamente na subida do container.

---

## 🐳 Deploy com Docker em qualquer servidor

### Pré-requisitos

- **Docker** (24+)
- **Docker Compose** (v2+)
- **Git** (ou copie os arquivos manualmente)

### Passo a passo

#### 1. Leve o projeto para o servidor

```bash
# Opção A: clonando
git clone https://github.com/MartinsSallys/BeckGlobal.git
cd BeckGlobal

# Opção B: copiando os arquivos (zip, rsync, scp, etc.)
scp -r BeckGlobal/ user@servidor:/caminho/deploy/
ssh user@servidor
cd /caminho/deploy/BeckGlobal
```

#### 2. Configure o `.env`

```bash
cp .env.example .env
```

Edite o `.env` com valores reais para produção:

```bash
# ⚠️ OBRIGATÓRIO mudar em produção:
SECRET_KEY=uma-chave-longa-e-aleatoria  # gere com: openssl rand -hex 32
```

Dentro do Docker Compose, o `DATABASE_URL` é **sobrescrito automaticamente**
para apontar para o host `db` (veja `docker-compose.yml`). O valor no `.env`
serve para execução local (sem Docker).

#### 3. Suba os containers

```bash
docker compose up -d --build
```

Isso sobe 2 containers:
- **app**: API FastAPI na porta 8000 (roda `alembic upgrade head` antes de iniciar)
- **db**: PostgreSQL 16 na porta 5432 com volume persistente

#### 4. Verifique se tudo subiu

```bash
docker compose ps
docker compose logs -f app
curl http://localhost:8000/health
```

### Atualizando o deploy

```bash
git pull
docker compose up -d --build
```

### Parando tudo

```bash
docker compose down          # mantém o volume do banco
docker compose down -v       # remove TUDO, inclusive os dados
```

---

## 🛠 Deploy sem Docker (modo tradicional)

### Pré-requisitos

- Python 3.12+
- Poetry
- PostgreSQL 16 instalado e rodando

### Banco de dados

```bash
sudo -u postgres psql
```

```sql
CREATE USER usuario WITH PASSWORD 'senha';
CREATE DATABASE beckglobal OWNER usuario;
\q
```

### Instalação e execução

```bash
git clone https://github.com/MartinsSallys/BeckGlobal.git
cd BeckGlobal
cp .env.example .env

# Edite o .env com os dados do seu PostgreSQL local:
# DATABASE_URL=postgresql+psycopg://usuario:senha@localhost:5432/beckglobal

poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

API em `http://localhost:8000`.

---

## 🔐 Autenticação

O fluxo é baseado em JWT (Bearer token):

1. `POST /users/` — cria um usuário (público).
2. `POST /auth/token` — login via `application/x-www-form-urlencoded`
   (`username` = e-mail, `password` = senha). Retorna `access_token`.
3. Rotas de `GET/PUT/DELETE /users` exigem `Authorization: Bearer <token>`.

Exemplo:

```bash
curl -X POST http://localhost:8000/users/ \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alice","email":"alice@example.com","password":"secret123"}'

curl -X POST http://localhost:8000/auth/token \
  -d 'username=alice@example.com&password=secret123'
```

No Swagger (`/docs`), use o botão **Authorize** com o token retornado.

Regras atuais:
- `PUT` e `DELETE` só permitem alterar/remover a própria conta.
- Senha com mínimo de 8 caracteres.
- E-mails são normalizados para minúsculas.

---

## 🗄 Banco de dados e Migrations

### Criar nova migration

```bash
poetry run alembic revision --autogenerate -m "descricao da mudanca"
```

### Aplicar migrations

```bash
poetry run alembic upgrade head
```

### Reverter última migration

```bash
poetry run alembic downgrade -1
```

### Ver histórico

```bash
poetry run alembic history
```

> Novos modelos precisam ser importados em `app/models/__init__.py` para que o
> Alembic os detecte no autogenerate.

---

## 🧪 Testes

Os testes usam SQLite in-memory, então não precisam de um PostgreSQL rodando.

```bash
task test
```

Equivalente a:

```bash
poetry run pytest -s -x --cov=app -vv
```

A cobertura mínima configurada é de 80%.

---

## 🎨 Qualidade de Código

```bash
task format     # formata o código (ruff)
task lint       # verifica formato e estilo (ruff)
task typecheck  # verifica tipos (mypy)
```

Ou via Makefile:

```bash
make lint
make format
make typecheck
make test
```

---

## 📖 Documentação da API

```text
Swagger:  http://localhost:8000/docs
ReDoc:    http://localhost:8000/redoc
Health:   http://localhost:8000/health
```

`GET /health` retorna `200` quando o banco está acessível e `503` quando não
está (útil para readiness/liveness probes).

---

## 📌 Arquitetura

Estrutura enxuta em camadas:

```
Request → Router (app/api) → Session/Model (app/database + app/models) → Response
```

- **API**: recebe e valida requisições HTTP (schemas + routers).
- **Core**: configuração, logging, exceções e segurança.
- **Database**: engine, sessão e `Base` do SQLAlchemy.
- **Models**: modelos de persistência (PostgreSQL via SQLAlchemy).

---

## ✅ Recursos

- Autenticação JWT com rotas protegidas
- Registro e CRUD de usuários
- Senhas com hash bcrypt
- Configuração via `.env`
- Logging centralizado
- Tratamento global de exceções
- SQLAlchemy 2.0 + PostgreSQL
- Alembic para migrations
- Docker & Docker Compose com healthcheck e execução de migrations
- Testes automatizados com cobertura (SQLite in-memory)
- Lint, formatação e type checking
- Pre-commit hooks

---

## 📌 Roadmap

- [ ] Refresh Token
- [ ] Papéis/permissões (RBAC)
- [ ] Redis / Cache
- [ ] Celery
- [ ] Rate Limit
- [ ] OpenTelemetry
- [ ] GitHub Actions (CI/CD)
- [ ] Deploy automático

---

## 🤝 Contribuindo

1. Fork
2. Crie sua branch: `git checkout -b minha-feature`
3. Commit: `git commit -m 'feat: minha feature'`
4. Push: `git push origin minha-feature`
5. Abra um Pull Request

---

## 📄 Licença

MIT
