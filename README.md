# BeckGlobal

Boilerplate de API em Python com FastAPI, PostgreSQL, autenticação JWT, migrations e testes automatizados. Pronto para ser usado como base de novos projetos por qualquer dev.

> Documentação de handoff mais detalhada: [`docs/PROJETO.md`](docs/PROJETO.md).

---

## Sumário

- [O que vem pronto](#o-que-vem-pronto)
- [Stack](#stack)
- [Requisitos](#requisitos)
- [Início rápido com Docker](#início-rápido-com-docker)
- [Rodando localmente](#rodando-localmente)
- [Configuração](#configuração)
- [Endpoints](#endpoints)
- [Autenticação](#autenticação)
- [Banco de dados e migrations](#banco-de-dados-e-migrations)
- [Testes](#testes)
- [Qualidade de código](#qualidade-de-código)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Arquitetura](#arquitetura)
- [Docker](#docker)
- [Usando como template](#usando-como-template)
- [Checklist de produção](#checklist-de-produção)
- [Roadmap](#roadmap)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## O que vem pronto

- [x] Aplicação FastAPI com CORS, logging e tratamento global de exceções
- [x] Configuração via variáveis de ambiente (`.env`) com Pydantic Settings
- [x] SQLAlchemy 2.0 + PostgreSQL
- [x] Alembic configurado com migration inicial real
- [x] Autenticação JWT (`POST /auth/token`) e rotas protegidas
- [x] Hash de senha com bcrypt
- [x] CRUD de usuários com validações e regras de permissão
- [x] Health check com status do banco (200/503)
- [x] Suite de testes com SQLite in-memory e cobertura mínima de 80%
- [x] Docker + Docker Compose com healthcheck e migrations automáticas
- [x] Dockerfile non-root com apenas dependências de produção
- [x] Ruff, MyPy, Pre-commit, Taskipy e Makefile
- [x] README e documentação de handoff

---

## Stack

| Camada | Tecnologia |
|---|---|
| Runtime | Python 3.12+ |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Banco | PostgreSQL 16 (psycopg 3) |
| Migrations | Alembic |
| Dependências | Poetry |
| Auth | PyJWT + bcrypt |
| Validação/config | Pydantic v2 + pydantic-settings |
| Testes | Pytest + pytest-cov |
| Qualidade | Ruff, MyPy, Pre-commit |
| Infra | Docker, Docker Compose |

---

## Requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- PostgreSQL 16 (ou Docker)
- Docker + Docker Compose (opcional, mas recomendado)

---

## Início rápido com Docker

```bash
git clone https://github.com/MartinsSallys/BeckGlobal.git
cd BeckGlobal
cp .env.example .env
docker compose up -d --build
```

Serviços disponíveis após a subida:

| Serviço | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health check | http://localhost:8000/health |

As migrations são aplicadas automaticamente antes do servidor iniciar.

Acompanhe os logs:

```bash
docker compose logs -f app
```

Para parar:

```bash
docker compose down      # mantém os dados do banco
docker compose down -v   # remove tudo, inclusive os dados
```

---

## Rodando localmente

Sem Docker, com PostgreSQL instalado na máquina:

```bash
# 1) criar usuário e banco
sudo -u postgres psql
```

```sql
CREATE USER usuario WITH PASSWORD 'senha';
CREATE DATABASE beckglobal OWNER usuario;
\q
```

```bash
# 2) instalar dependências
cp .env.example .env
poetry install

# 3) aplicar migrations
poetry run alembic upgrade head

# 4) subir a API
poetry run uvicorn app.main:app --reload
```

Ajuste o `DATABASE_URL` no `.env` conforme o seu PostgreSQL local.

---

## Configuração

Todas as configurações vêm de variáveis de ambiente (arquivo `.env`):

| Variável | Descrição | Padrão |
|---|---|---|
| `APP_NAME` | Nome exibido na documentação | `Backend Boilerplate` |
| `DEBUG` | Ativa logs de debug | `False` |
| `DATABASE_URL` | URL de conexão do banco | `postgresql+psycopg://usuario:senha@localhost:5432/beckglobal` |
| `SECRET_KEY` | Chave de assinatura do JWT | vazio — **troque em produção** |
| `ALGORITHM` | Algoritmo do JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo de expiração do token | `30` |
| `CORS_ORIGINS` | Origens permitidas (JSON) | `["*"]` |

Gere uma chave segura com:

```bash
openssl rand -hex 32
```

> No Docker Compose, o `DATABASE_URL` é sobrescrito para apontar ao host `db`.

---

## Endpoints

| Método | Rota | Autenticação | Descrição |
|---|---|---|---|
| `GET` | `/health` | Não | Status da aplicação e do banco |
| `POST` | `/users/` | Não | Registro de usuário |
| `POST` | `/auth/token` | Não | Login (retorna access token) |
| `GET` | `/users/` | Bearer | Lista usuários (`skip`, `limit`) |
| `GET` | `/users/{id}` | Bearer | Busca usuário por ID |
| `PUT` | `/users/{id}` | Bearer | Atualiza a própria conta |
| `DELETE` | `/users/{id}` | Bearer | Remove a própria conta |

---

## Autenticação

O fluxo usa JWT no header `Authorization: Bearer <token>`.

```bash
# 1) registrar
curl -X POST http://localhost:8000/users/ \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alice","email":"alice@example.com","password":"secret123"}'

# 2) login
curl -X POST http://localhost:8000/auth/token \
  -d 'username=alice@example.com&password=secret123'

# 3) acessar rota protegida
curl http://localhost:8000/users/ \
  -H 'Authorization: Bearer <ACCESS_TOKEN>'
```

No Swagger (`/docs`), clique em **Authorize** e informe o token.

Regras atuais:

- Senha com mínimo de 8 caracteres.
- E-mails são normalizados para minúsculas.
- E-mail duplicado retorna `409 Conflict`.
- `PUT` e `DELETE` só afetam a própria conta (`403` caso contrário).
- Usuário inativo não autentica (`403`) e token inválido retorna `401`.
- Senhas são armazenadas com hash bcrypt.

---

## Banco de dados e migrations

```bash
# aplicar todas as migrations
poetry run alembic upgrade head

# criar uma migration a partir dos models
poetry run alembic revision --autogenerate -m "descricao da mudanca"

# reverter a última migration
poetry run alembic downgrade -1

# histórico
poetry run alembic history
```

> Novos models devem ser exportados em `app/models/__init__.py` para serem
> detectados pelo `autogenerate`.

---

## Testes

Os testes usam SQLite in-memory, portanto não exigem PostgreSQL rodando.

```bash
task test
```

Equivalente a:

```bash
poetry run pytest -s -x --cov=app -vv
```

Cobertura atual: 18 testes e ~89% de cobertura (mínimo configurado: 80%).

---

## Qualidade de código

```bash
task lint       # ruff format --check + ruff check
task format     # ruff format
task typecheck  # mypy
```

Atalhos também disponíveis no Makefile:

```bash
make lint
make format
make typecheck
make test
```

Pre-commit configurado com Ruff, trailing whitespace, end-of-file, check-yaml e
check-merge-conflict.

---

## Estrutura do projeto

```text
.
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py       # login / JWT
│   │   │   ├── health.py     # health check
│   │   │   └── users.py      # CRUD de usuários
│   │   ├── dependencies.py   # usuário autenticado
│   │   ├── router.py         # registro dos routers
│   │   └── schemas.py        # schemas Pydantic
│   ├── core/
│   │   ├── config.py         # settings / .env
│   │   ├── exception.py      # exceções e handler global
│   │   ├── logging_config.py # logging
│   │   └── security.py       # bcrypt + JWT
│   ├── database/
│   │   ├── base.py           # DeclarativeBase
│   │   ├── connection.py     # engine e SessionLocal
│   │   └── session.py        # dependência get_db
│   ├── models/
│   │   └── user.py           # model User
│   └── main.py               # instância FastAPI
├── alembic/                  # migrations
├── tests/                    # testes (SQLite in-memory)
├── docs/PROJETO.md           # documentação de handoff
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Arquitetura

Estrutura enxuta em camadas:

```text
Request -> Router (app/api) -> Session/Model (app/database + app/models) -> Response
```

- **API**: recebe e valida requisições (schemas + routers).
- **Core**: configuração, logging, exceções e segurança.
- **Database**: engine, sessão e `Base` do SQLAlchemy.
- **Models**: persistência no PostgreSQL via SQLAlchemy.

A arquitetura evita camadas extras de service/repository de propósito, mantendo o
boilerplate simples de entender e evoluir.

---

## Docker

- **Dockerfile**: instala apenas dependências de produção (`--only main`), roda
  como usuário não-root, expõe a porta 8000 e possui `HEALTHCHECK`.
- **docker-compose.yml**: serviços `app` e `db` (PostgreSQL 16 com volume
  persistente), healthcheck do banco, `depends_on` com `condition:
  service_healthy`, `restart: unless-stopped` e migrations automáticas no start.
- **.dockerignore**: mantém `.env`, `.git`, banco local, caches e testes fora da
  imagem.

---

## Usando como template

1. Crie um repositório novo e copie os arquivos (ou use "Use this template" no GitHub).
2. Renomeie o projeto em `pyproject.toml` (`name`) e ajuste `APP_NAME`.
3. Troque `SECRET_KEY`, `DATABASE_URL` e as credenciais do Postgres.
4. Ajuste CORS para os domínios reais.
5. Adicione seus models em `app/models/` e exporte em `app/models/__init__.py`.
6. Gere a migration: `poetry run alembic revision --autogenerate -m "..."`.
7. Rode `task test` e `task lint` antes de abrir o PR.

---

## Checklist de produção

- [ ] Trocar `SECRET_KEY` por uma chave aleatória forte
- [ ] Definir `DEBUG=False`
- [ ] Restringir `CORS_ORIGINS` aos domínios reais
- [ ] Trocar as credenciais do PostgreSQL
- [ ] Configurar HTTPS/reverse proxy (nginx, traefik, etc.)
- [ ] Configurar backup do volume `pgdata`
- [ ] Adicionar CI/CD (GitHub Actions)

---

## Roadmap

- [ ] Refresh Token
- [ ] Papéis e permissões (RBAC)
- [ ] Redis / Cache
- [ ] Celery
- [ ] Rate Limit
- [ ] OpenTelemetry
- [ ] GitHub Actions (CI/CD)
- [ ] Deploy automático

---

## Contribuindo

1. Faça um fork
2. Crie uma branch: `git checkout -b minha-feature`
3. Commit: `git commit -m 'feat: minha feature'`
4. Push: `git push origin minha-feature`
5. Abra um Pull Request

Antes de contribuir, rode:

```bash
task lint
task typecheck
task test
```

---

## Licença

MIT
