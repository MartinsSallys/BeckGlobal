# Guia do Projeto — BeckGlobal

Documento de handoff do boilerplate de API em FastAPI. Pode ser compartilhado
com o time como referência rápida.

---

## 1. Visão geral

BeckGlobal é um boilerplate para APIs REST em Python, pensado para ser base de
novos projetos. Entrega autenticação JWT, CRUD de usuários, migrations,
containerização e testes automatizados — tudo já configurado e passando.

- **Linguagem:** Python 3.12+
- **Framework:** FastAPI
- **Banco:** PostgreSQL 16 (SQLAlchemy 2.0 + psycopg)
- **Migrations:** Alembic
- **Dependências:** Poetry
- **Infra:** Docker + Docker Compose
- **Qualidade:** Ruff, MyPy, Pre-commit, Pytest + Coverage

---

## 2. Estrutura de pastas

```text
.
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py       # POST /auth/token (login)
│   │   │   ├── health.py     # GET /health
│   │   │   └── users.py      # CRUD de usuários
│   │   ├── dependencies.py   # get_current_user (JWT)
│   │   ├── router.py         # registro dos routers
│   │   ├── schemas.py        # schemas Pydantic
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py         # Settings (pydantic-settings / .env)
│   │   ├── exception.py      # AppException + handler global
│   │   ├── logging_config.py # logging centralizado
│   │   └── security.py       # hash bcrypt + JWT
│   ├── database/
│   │   ├── base.py           # DeclarativeBase
│   │   ├── connection.py     # engine + SessionLocal
│   │   └── session.py        # dependência get_db
│   ├── models/
│   │   └── user.py           # model User
│   └── main.py               # instância FastAPI, CORS, lifespan
├── alembic/
│   ├── env.py
│   └── versions/             # migrations
├── tests/
│   ├── conftest.py           # SQLite in-memory + fixtures
│   ├── test_auth.py
│   ├── test_health.py
│   └── test_users.py
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 3. Como rodar

### Com Docker (recomendado)

```bash
cp .env.example .env
docker compose up -d --build
```

- API: <http://localhost:8000>
- Swagger: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>

O container da app roda `alembic upgrade head` automaticamente antes de subir o
uvicorn. Dentro do Compose, o `DATABASE_URL` aponta para o host `db` (o valor do
`.env` é sobrescrito pelo `docker-compose.yml`).

### Sem Docker

```bash
cp .env.example .env
# ajuste DATABASE_URL para seu PostgreSQL local
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

---

## 4. Configuração (`.env`)

| Variável | Descrição | Padrão |
|---|---|---|
| `APP_NAME` | Nome exibido na doc | `Backend Boilerplate` |
| `DEBUG` | Log level DEBUG | `False` |
| `DATABASE_URL` | URL do banco | `postgresql+psycopg://usuario:senha@localhost:5432/beckglobal` |
| `SECRET_KEY` | Chave de assinatura JWT | vazio (troque!) |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do token | `30` |
| `CORS_ORIGINS` | Origens permitidas (JSON) | `["*"]` |

Gere a chave de produção com `openssl rand -hex 32`.

---

## 5. Endpoints

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| GET | `/health` | Não | Status da app e do banco (200/503) |
| POST | `/users/` | Não | Registro de usuário |
| POST | `/auth/token` | Não | Login (form: `username` = e-mail, `password`) |
| GET | `/users/` | Bearer | Lista usuários (`skip`, `limit`) |
| GET | `/users/{id}` | Bearer | Busca usuário |
| PUT | `/users/{id}` | Bearer | Atualiza a própria conta |
| DELETE | `/users/{id}` | Bearer | Remove a própria conta |

### Fluxo de autenticação

```bash
# 1) registrar
curl -X POST http://localhost:8000/users/ \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alice","email":"alice@example.com","password":"secret123"}'

# 2) login
curl -X POST http://localhost:8000/auth/token \
  -d 'username=alice@example.com&password=secret123'

# 3) usar o token
curl http://localhost:8000/users/ \
  -H 'Authorization: Bearer <ACCESS_TOKEN>'
```

No Swagger, use **Authorize** com o token retornado.

### Regras de negócio atuais

- Senha mínima de 8 caracteres.
- E-mail normalizado para minúsculas.
- E-mail duplicado retorna **409** (inclusive no update).
- `PUT`/`DELETE` só podem afetar a própria conta (**403** caso contrário).
- Usuário inativo não consegue autenticar (**403**) nem usar token (**401**).
- Senhas armazenadas com hash bcrypt (nunca em texto puro).

---

## 6. Banco de dados e migrations

```bash
# aplicar
poetry run alembic upgrade head

# criar após alterar models
poetry run alembic revision --autogenerate -m "descricao"

# reverter a última
poetry run alembic downgrade -1
```

> Importante: novos models devem ser exportados em `app/models/__init__.py`
> para entrarem no `Base.metadata` e serem detectados pelo autogenerate.

---

## 7. Testes

Os testes usam **SQLite in-memory** com override da dependência `get_db`, então
não exigem PostgreSQL rodando.

```bash
task test
# equivale a: poetry run pytest -s -x --cov=app -vv
```

Cobertura atual: **18 testes, ~89% de cobertura** (mínimo exigido: 80%).
Cobrem health, registro, validações, login, rotas protegidas, permissões e CRUD.

---

## 8. Qualidade de código

```bash
task format     # ruff format
task lint       # ruff format --check + ruff check
task typecheck  # mypy
```

Atalhos no Makefile: `make lint`, `make format`, `make typecheck`, `make test`.
Pre-commit configurado com ruff, trailing whitespace, EOF fixer, check-yaml e
check-merge-conflict.

---

## 9. Docker

- **Dockerfile**: instala apenas dependências de produção (`--only main`), roda
  como usuário não-root, expõe 8000 e tem `HEALTHCHECK` no `/health`.
- **docker-compose.yml**: serviços `app` + `db` (PostgreSQL 16 com volume
  `pgdata`), healthcheck do banco, `depends_on` com `condition: service_healthy`,
  `restart: unless-stopped` e migrations automáticas no start.
- **`.dockerignore`**: evita copiar `.env`, `.git`, `dev.db`, caches e testes para
  a imagem.

---

## 10. Decisões e convenções

- Arquitetura enxuta: `router → schema → session/model`. Sem camadas extras de
  service/repository por enquanto (evita complexidade prematura).
- Configuração 100% via variáveis de ambiente/`.env`.
- Erros de negócio retornam `HTTPException` com códigos HTTP explícitos.
- `AppException` + handler global disponíveis para exceções customizadas.
- Tipagem forte (mypy) e estilo único (ruff, aspas simples).

---

## 11. Checklist antes de usar em produção

- [ ] Trocar `SECRET_KEY` por uma chave aleatória forte.
- [ ] Definir `DEBUG=False`.
- [ ] Restringir `CORS_ORIGINS` aos domínios reais.
- [ ] Trocar as credenciais do PostgreSQL no `docker-compose.yml`.
- [ ] Configurar HTTPS/reverse proxy (nginx, traefik, etc.).
- [ ] Configurar backup do volume `pgdata`.
- [ ] Adicionar CI/CD (GitHub Actions) — ainda no roadmap.

---

## 12. Roadmap

- [ ] Refresh Token
- [ ] Papéis/permissões (RBAC)
- [ ] Redis / Cache
- [ ] Celery
- [ ] Rate Limit
- [ ] OpenTelemetry
- [ ] GitHub Actions (CI/CD)
- [ ] Deploy automático

---

## 13. Correções aplicadas nesta revisão

- Migration inicial vazia corrigida (tabela `users` agora é criada).
- `alembic/env.py` passou a importar os models no metadata.
- Autenticação JWT implementada de fato (`/auth/token` + rotas protegidas).
- `get_current_user` agora consulta o banco (antes só devolvia um dict).
- Docker Compose corrigido (host `db`, migrations automáticas, healthcheck).
- Dockerfile endurecido (non-root, só deps de produção, healthcheck).
- Testes automatizados criados do zero (18 testes, SQLite in-memory).
- `.env`, `dev.db` e `__pycache__` removidos do versionamento.
- Taskipy/Makefile/pre-commit/mypy/coverage alinhados e funcionando.
- README reescrito para refletir o código real.
