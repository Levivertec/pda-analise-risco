# 🛠️ Manual do Desenvolvedor — Calculadora PDA (NBR 5419-2:2026)

> **Objetivo deste documento:** permitir que **qualquer desenvolvedor** reconstrua,
> mantenha e evolua o aplicativo **a qualquer tempo, sem depender do autor original
> nem de nenhuma ferramenta de IA específica**. Se este projeto precisar ser retomado
> por outra pessoa, este é o ponto de partida.
>
> **Regra de manutenção:** este documento DEVE ser revisado ao final de cada sprint.
> Tudo que sair de operação ou for modificado deve ser atualizado aqui. Itens
> descontinuados vão para a seção [Histórico de mudanças](#15-histórico-de-mudanças).

**Versão do documento:** 1.0
**Última atualização:** 01/05/2026
**Mantenedor atual:** Levi Carvalho (`levi@vertecenergia.com`)

---

## Índice

1. [Visão geral do produto](#1-visão-geral-do-produto)
2. [Stack tecnológica](#2-stack-tecnológica)
3. [Arquitetura (atual e alvo)](#3-arquitetura-atual-e-alvo)
4. [Estrutura de arquivos](#4-estrutura-de-arquivos)
5. [Ambiente local — como rodar do zero](#5-ambiente-local--como-rodar-do-zero)
6. [O motor de cálculo (norma → código)](#6-o-motor-de-cálculo-norma--código)
7. [Autenticação e controle de acesso](#7-autenticação-e-controle-de-acesso)
8. [Base de dados NG (Anexo F)](#8-base-de-dados-ng-anexo-f)
9. [Geração de relatórios (PDF/DOCX)](#9-geração-de-relatórios-pdfdocx)
10. [Ambientes: Teste e Produção](#10-ambientes-teste-e-produção)
11. [Deploy (Streamlit Cloud)](#11-deploy-streamlit-cloud)
12. [Banco de dados (Railway) — arquitetura-alvo](#12-banco-de-dados-railway--arquitetura-alvo)
13. [Segurança e segredos](#13-segurança-e-segredos)
14. [Metodologia de sprints](#14-metodologia-de-sprints)
15. [Histórico de mudanças](#15-histórico-de-mudanças)
16. [Lições aprendidas](#16-lições-aprendidas)
17. [Roadmap](#17-roadmap)

---

## 1. Visão geral do produto

**Calculadora PDA** é um aplicativo web para **análise de risco de Proteção contra
Descargas Atmosféricas (SPDA)** conforme a **ABNT NBR 5419-2:2026** (Parte 2 — Análise
de risco).

O público-alvo são **engenheiros e técnicos projetistas de SPDA**. O app guia o usuário
na entrada de dados de uma estrutura e calcula automaticamente os riscos normativos,
comparando-os com os riscos toleráveis e gerando um **memorial de cálculo** exportável.

**O que o app calcula:**
- **R1** — Risco de perda de vida humana
- **R3** — Risco de perda de patrimônio cultural
- **R4** — Risco de perda de valor econômico (Anexo D, informativo)
- **Frequência de danos F** (Seção 7) — *em roadmap para exposição na UI*

**Saídas:** dashboard interativo + memorial em PDF, Word e Markdown.

---

## 2. Stack tecnológica

| Camada | Tecnologia | Versão | Por quê |
|---|---|---|---|
| Linguagem | Python | 3.11 (prod) / 3.14 (dev local) | Streamlit Cloud roda 3.11 |
| Framework web | Streamlit | ≥ 1.32 | Prototipagem rápida, deploy gratuito |
| Dados | pandas | ≥ 2.0 | Leitura do CSV de NG, tabelas |
| Gráficos | plotly | ≥ 5.18 | Dashboards interativos |
| PDF | reportlab | ≥ 4.0 | Memorial em PDF |
| DOCX | python-docx | ≥ 1.1 | Memorial em Word |
| Hospedagem | Streamlit Community Cloud | — | Gratuito, deploy via Git |
| Banco (alvo) | PostgreSQL @ Railway | — | Persistência de usuários/auditoria |
| Versionamento | Git + GitHub | — | Repositório `Levivertec/pda-analise-risco` |

> ⚠️ **Não usar recursos de Python > 3.11** no código de produção. O Streamlit Cloud
> usa 3.11. Recursos de 3.12+ quebram o deploy.

---

## 3. Arquitetura (atual e alvo)

### 3.1 Arquitetura ATUAL (em operação)

```
Navegador
   │
   ▼
Streamlit Community Cloud  ──  app.py (UI)
   │                              │
   │                              ▼
   │                        src/nbr5419/  (motor puro, sem Streamlit)
   │                              ├── modelo.py   (dataclasses)
   │                              ├── tabelas.py  (constantes da norma)
   │                              ├── calculo.py  (fórmulas)
   │                              ├── auth.py     (login/roles)
   │                              └── relatorio.py(PDF/DOCX)
   │
   ▼
st.secrets  ──  [auth_hashes] / [auth_expira] / [auth_roles]  (READ-ONLY)
data/ng_municipios.csv  (base NG, 5.571 municípios)
```

**Princípio de design:** o **motor de cálculo (`src/nbr5419/`) é puro Python**, sem
nenhuma dependência do Streamlit. A UI (`app.py`) apenas consome o motor. Isso permite
reaproveitar o motor em outras interfaces (CLI, API REST, desktop) no futuro.

### 3.2 Arquitetura ALVO (em implantação — Sprint 0+)

**Decisão (Sprint 0):** hospedagem migra do Streamlit Community Cloud para o **Railway**
(conta paga do usuário), em um **projeto isolado** (`calculadora-pda`) com **dois
ambientes** (production e test). Motivos: sem cold start, app + banco no mesmo lugar,
domínio próprio, privado e robusto para a fase comercial.

```
            ┌──────────────────────────────────────┐
            │ GitHub: Levivertec/pda-analise-risco  │
            │   branch main    ───► PRODUÇÃO         │
            │   branch develop ───► TESTE            │
            └──────────────────────────────────────┘
                     │                    │
                     ▼                    ▼
        ┌─ Railway projeto: calculadora-pda ──────────────┐
        │  Environment "production"   Environment "test"   │
        │   ├── app (Streamlit)        ├── app (Streamlit) │
        │   └── PostgreSQL             └── PostgreSQL       │
        └─────────────────────────────────────────────────┘
                     │
                     ▼
        Domínio: pda.tesconsult.com.br (produção)
```

> O Streamlit Community Cloud (`pda-nbr5419-ar.streamlit.app`) fica como **fallback
> histórico** até a migração ser validada; depois pode ser desativado.

Ver detalhes em [Seção 10](#10-ambientes-teste-e-produção), [Seção 11](#11-deploy-streamlit-cloud)
e [Seção 12](#12-banco-de-dados-railway--arquitetura-alvo).

---

## 4. Estrutura de arquivos

```
.
├── app.py                       # UI Streamlit (wizard 6 etapas + painel admin) ~1300 linhas
├── teste_exemplo.py             # Smoke test do motor (sem UI)
├── requirements.txt             # Dependências Python
├── deploy.bat                   # Atalho: git add+commit+push
│
├── src/nbr5419/                 # MOTOR — Python puro, sem Streamlit
│   ├── __init__.py              # Exporta API pública do pacote
│   ├── modelo.py                # Dataclasses: Projeto, Estrutura, Zona, Linha + enums
│   ├── tabelas.py               # TODAS as constantes normativas (Tabelas A.1 a F.1)
│   ├── calculo.py               # Fórmulas: áreas, N, P, L, componentes RA-RZ, R1-R4
│   ├── auth.py                  # Login, hash de senha, roles, expiração
│   └── relatorio.py             # Geração de memorial PDF (reportlab) e DOCX (python-docx)
│
├── scripts/                     # Ferramentas de linha de comando (uso do admin)
│   ├── gerar_hash.py            # Gera hash PBKDF2 de uma senha
│   ├── gerenciar_acessos.py     # CLI: listar/add/revogar/renovar/promover usuários
│   ├── gerar_emails.py          # Gera arquivos .eml de convite
│   └── gerar_icone.py           # Gera ícone de raio (PNG/ICO)
│
├── data/
│   └── ng_municipios.csv        # NG por município (Anexo F) — 5.571 entradas
│
├── assets/
│   ├── icone_raio.ico           # Ícone (atalho desktop, PWA)
│   └── icone_raio.png           # Ícone (web/favicon)
│
├── .streamlit/
│   ├── config.toml              # Tema visual (azul #1f4e79)
│   ├── secrets.toml             # ⚠️ GITIGNORED — hashes/roles/expira (e futuramente DATABASE_URL)
│   └── secrets.example.toml     # Template público (sem segredos reais)
│
├── .devcontainer/
│   └── devcontainer.json        # Config GitHub Codespaces (Python 3.11)
│
└── Documentação (.md)
    ├── README.md                # Visão geral rápida
    ├── MANUAL_DESENVOLVEDOR.md  # ESTE arquivo
    ├── MANUAL_USUARIO.md        # Manual do usuário final
    ├── DEPLOY.md                # Passo-a-passo do primeiro deploy
    ├── OPERACAO.md              # Operação dia-a-dia (gestão de acessos)
    └── PASSO_A_PASSO.md         # Ciclo de vida do produto em fases
```

**Arquivos NUNCA versionados** (protegidos pelo `.gitignore`):
`.streamlit/secrets.toml`, `credenciais.txt`, `emails/`, `Projetos/`, `*.pdf` (exceto `assets/`).

---

## 5. Ambiente local — como rodar do zero

### 5.1 Pré-requisitos
- **Python 3.11+** (em produção é 3.11; localmente pode ser mais novo)
- **Git** instalado
- Sistema operacional: Windows (instruções abaixo) — adaptável a Linux/Mac

### 5.2 Clonar e instalar

```bash
git clone https://github.com/Levivertec/pda-analise-risco.git
cd pda-analise-risco
pip install -r requirements.txt
```

### 5.3 Configurar segredos locais

Crie `.streamlit/secrets.toml` a partir do template:

```toml
[auth_hashes]
"seu.email@empresa.com" = "<hash gerado por scripts/gerar_hash.py>"

[auth_expira]
"seu.email@empresa.com" = "2099-12-31"

[auth_roles]
"seu.email@empresa.com" = "admin"
```

Para gerar um hash: `python scripts/gerar_hash.py`

### 5.4 Rodar

No **Windows**, sempre forçar UTF-8 antes (evita erro de acentuação):

```powershell
# PowerShell
$env:PYTHONUTF8="1"
python -m streamlit run app.py
```

```cmd
:: CMD
set PYTHONUTF8=1
python -m streamlit run app.py
```

Abre em `http://localhost:8501`.

### 5.5 Testar o motor sem UI

```bash
python teste_exemplo.py
```

Deve terminar com `[OK] Todos os sanity checks passaram.`

---

## 6. O motor de cálculo (norma → código)

A equação geral da norma é:

> **Rₓ = Nₓ × Pₓ × Lₓ**  (Eq. 3 da NBR 5419-2)

Onde, para cada componente:
- **N** = número anual de eventos perigosos (Anexo A)
- **P** = probabilidade de dano (Anexo B)
- **L** = quantidade de perda (Anexo C / D)

### 6.1 Os 8 componentes de risco

| Componente | Fonte | Tipo de dano | Fórmula |
|---|---|---|---|
| RA | S1 (descarga na estrutura) | D1 (ferimentos) | ND × PA × LA |
| RB | S1 | D2 (danos físicos) | ND × PB × LB |
| RC | S1 | D3 (falha sist. internos) | ND × PC × LC |
| RM | S2 (descarga próxima) | D3 | NM × PM × LM |
| RU | S3 (descarga na linha) | D1 | (NL+NDJ) × PU × LU |
| RV | S3 | D2 | (NL+NDJ) × PV × LV |
| RW | S3 | D3 | (NL+NDJ) × PW × LW |
| RZ | S4 (descarga próx. linha) | D3 | NI × PZ × LZ |

### 6.2 Composição dos riscos
- **R1** = RA + RB + RC* + RM* + RU + RV + RW* + RZ*  (*só p/ explosão ou risco à vida)
- **R3** = RB + RV
- **R4** = todos os componentes (Anexo D)

### 6.3 Mapeamento código ↔ norma
- `calculo.py` → cada função tem docstring com a Equação/Seção de origem (A.1, B.2, C.3, etc.)
- `tabelas.py` → cada constante tem comentário com a Tabela de origem
- **Ao alterar qualquer valor, confira contra o PDF da norma** e rode `teste_exemplo.py`.

### 6.4 Fonte da norma
PDFs originais em: `C:\Users\LeviCarvalho\vertecenergia.com\Vertec - ENG - Documentos\
08. Biblioteca Virtual\NORMAS E RESOLUÇÕES\NORMAS\ABNT NBR\` (4 partes + erratas).

---

## 7. Autenticação e controle de acesso

### 7.1 Formato dos segredos (`secrets.toml` / Streamlit Cloud Secrets)

```toml
[auth_hashes]
"email@dominio.com" = "<hash_pbkdf2_sha256>"

[auth_expira]
"email@dominio.com" = "2099-12-31"   # YYYY-MM-DD; 2099-12-31 = acesso indeterminado

[auth_roles]
"email@dominio.com" = "admin"        # ou "user" (padrão)
```

### 7.2 Hash de senha
- Algoritmo: **PBKDF2-HMAC-SHA256, 100.000 iterações**
- **Salt = e-mail em minúsculas** (determinístico — permite recalcular sem armazenar salt)
- Função: `hash_senha(email, senha)` em `auth.py`

### 7.3 Roles
- `admin` — vê o **Painel Admin** (listar/cadastrar usuários, gerar TOML)
- `user` — acesso normal ao app
- Default quando não especificado: `user`

### 7.4 Expiração
- Cada usuário tem data de expiração. Login após a data → bloqueado automaticamente.
- `2099-12-31` = indeterminado (validação interna).
- Para uso comercial: data fim da assinatura.

### 7.5 ⚠️ DECISÕES CRÍTICAS — NÃO REGREDIR
1. **NÃO usar `hashlib.compare_digest`** com valores vindos de `st.secrets`. O Streamlit
   Cloud envolve os valores em wrappers e o `compare_digest` lança `AttributeError`.
   Use comparação `==` direta após `_coerce_str()`. (Ver [Lições Aprendidas](#16-lições-aprendidas).)
2. **NÃO usar TOML inline tables** (`{ hash="...", expira="..." }`). Quebra no Streamlit
   Cloud. Sempre seções paralelas (`[auth_hashes]`, `[auth_expira]`, `[auth_roles]`).
3. **Mudanças em usuários exigem sincronização manual** com o painel do Streamlit Cloud
   (Settings → Secrets → Save). O CLI só edita o arquivo local.

### 7.6 Gestão de acessos (CLI)
```bash
python scripts/gerenciar_acessos.py
# [1] listar  [2] adicionar  [3] revogar  [4] renovar
# [5] remover [6] promover/rebaixar  [7] migrar validação→data fixa
# [8] mostrar bloco TOML para colar no Streamlit Cloud
```

---

## 8. Base de dados NG (Anexo F)

- Arquivo: `data/ng_municipios.csv` (colunas: `municipio,uf,ng`)
- **5.571 municípios** (todos os do Brasil + DF/Brasília)
- **Fonte oficial:** planilha ABNT `Tabela_F1_NG_Municipios NBR5419_2026.xlsx`
  (em `...\07. Padrões\02. ENG Projetos\02. SPDA e Aterramento\1 Análise de Risco\`)
- ⚠️ A norma **exige** uso exclusivo dos valores do Anexo F. Não usar outras fontes.
- **Atualização:** se a ABNT publicar nova edição do Anexo F, reimportar a planilha
  oficial (ver Lição Aprendida sobre extração de PDF vs. planilha).

---

## 9. Geração de relatórios (PDF/DOCX)

- Módulo: `src/nbr5419/relatorio.py`
- `gerar_pdf(projeto, resultado)` → bytes (reportlab)
- `gerar_docx(projeto, resultado)` → bytes (python-docx)
- Estrutura do memorial: cabeçalho → estrutura → áreas/eventos → medidas → linhas →
  componentes por zona → conclusão (R vs RT) → diagnóstico
- Status colorido: vermelho se R > RT, verde se aceitável.

---

## 10. Ambientes: Teste e Produção

> **Princípio:** nenhuma alteração vai direto para os usuários. Tudo é validado em
> TESTE antes de promover para PRODUÇÃO.

### 10.1 Mapeamento (Railway)

| Ambiente | Railway Environment | Branch Git | Banco | Domínio | Público |
|---|---|---|---|---|---|
| **TESTE** | `test` | `develop` | PostgreSQL (env test) | `*.up.railway.app` | Projetistas/devs |
| **PRODUÇÃO** | `production` | `main` | PostgreSQL (env production) | `pda.tesconsult.com.br` | Clientes / uso estável |

Ambos no projeto Railway `calculadora-pda`. Cada Railway Environment é uma cópia
completa dos serviços (app + banco) com suas próprias variáveis de ambiente.

**Arquivos de configuração do Railway (no repositório):**
- `railway.json` — builder NIXPACKS + start command (`bash start.sh`)
- `start.sh` — gera `secrets.toml` a partir da env var `STREAMLIT_SECRETS_TOML` e sobe o Streamlit na `$PORT`
- `.python-version` — fixa Python 3.11

**Variáveis de ambiente por Railway Environment:**
- `STREAMLIT_SECRETS_TOML` — conteúdo TOML dos usuários (`[auth_hashes]`, `[auth_expira]`, `[auth_roles]`)
- `DATABASE_URL` — injetada automaticamente ao referenciar o serviço PostgreSQL (usada a partir do Sprint 1)

### 10.2 Fluxo de promoção (GitFlow simplificado)

```
feature/xxx ──► develop ──► (valida no app de TESTE) ──► main ──► (deploy automático em PROD)
```

1. Desenvolva em uma branch `feature/nome-da-feature` a partir de `develop`.
2. Abra PR para `develop`. Ao mergear, o app de **TESTE** atualiza automaticamente.
3. Teste exaustivamente no ambiente de teste (login, cálculo, relatório, admin).
4. Só depois de validado, abra PR de `develop` → `main`.
5. Ao mergear em `main`, o app de **PRODUÇÃO** atualiza automaticamente.

### 10.3 Regras
- **NUNCA** comitar direto em `main`.
- Cada ambiente tem **Secrets próprios** no Streamlit Cloud (apontando para o banco
  correto e com sua própria lista de usuários).
- Teste e Produção rodam **o mesmo código** — a diferença é só configuração (Secrets).

---

## 11. Deploy (Streamlit Cloud)

### 11.1 Criar um app
1. https://share.streamlit.io → **Create app** → from GitHub
2. Repository: `Levivertec/pda-analise-risco`
3. Branch: `main` (prod) ou `develop` (teste)
4. Main file: `app.py`
5. App URL: `calculadora-pda` (prod) ou `pda-nbr5419-ar` (teste)
6. **Advanced → Python 3.11**
7. **Advanced → Secrets:** colar o bloco TOML (ver Seção 7.1)
8. Deploy

> ⚠️ O subdomínio não pode conter a substring "anal" (filtro de profanidade do
> Streamlit). Por isso o teste usa `pda-nbr5419-ar` e não `pda-analise-risco`.

### 11.2 Atualizar (após o deploy inicial)
```bash
deploy.bat "mensagem do commit"      # ou: git add . && git commit -m "..." && git push
```
O Streamlit Cloud detecta o push e reimplanta em ~1-2 min.

### 11.3 Gerenciar app no ar
Botão **"Manage app"** (canto inferior direito) → logs, reboot, Settings (Secrets).

---

## 12. Banco de dados (Railway) — arquitetura-alvo

> **Status:** planejado (Sprint 1). Hoje a autenticação usa `st.secrets` (read-only),
> o que impede troca de senha self-service e auditoria. O banco resolve isso.

### 12.1 Projeto Railway
- **Projeto novo e isolado** dos demais (ex.: GED PIE Master): nome `calculadora-pda`
- Dois serviços PostgreSQL: `pda-test-db` e `pda-prod-db`
- Conta Railway: já paga (uso compartilhado com outros apps do usuário)

### 12.2 Schema inicial (proposto)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('admin','user')),
    expires_at DATE NOT NULL DEFAULT '2099-12-31',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_password_change TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    failed_login_attempts INT DEFAULT 0
);

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_email VARCHAR(255),
    action VARCHAR(50),
    details JSONB
);
```

### 12.3 Conexão
- `DATABASE_URL` fica nos Secrets de cada app Streamlit (teste→test-db, prod→prod-db)
- Driver: `psycopg2-binary` (adicionar ao `requirements.txt`)
- Migração: `scripts/migrar_para_postgres.py` (lê `secrets.toml` e popula `users`)
- **Fallback de transição:** durante a migração, `auth.py` tenta o banco e, se falhar,
  cai para `st.secrets` — permite rollback instantâneo.

---

## 13. Segurança e segredos

| Item | Onde fica | Versionado? |
|---|---|---|
| Hashes de senha | `secrets.toml` (local) + Streamlit Cloud Secrets | ❌ Nunca |
| Senhas em texto plano | `credenciais.txt` (local) | ❌ Nunca |
| `DATABASE_URL` (futuro) | Streamlit Cloud Secrets | ❌ Nunca |
| Código-fonte | GitHub (repositório **público**) | ✅ |

### Pontos de atenção
- O **repositório é público.** Para fase comercial, avaliar torná-lo privado
  (ver [Roadmap](#17-roadmap) e auditoria).
- Senhas iniciais foram geradas e distribuídas; **trocar após a validação**.
- Nunca enviar senha pelo mesmo canal do login (e-mail = login; Teams/WhatsApp = senha).

---

## 14. Metodologia de sprints

### 14.0 Premissas de governança (REGRA DE OURO)

> Estas premissas valem para **toda** a vida do projeto e têm precedência sobre
> conveniência ou velocidade de entrega.

1. **Toda mudança nasce no ambiente de TESTE**, nunca direto em produção. Produção
   só recebe o que já foi validado em teste. Objetivo: o software **nunca** fica
   indisponível para os usuários por causa de uma melhoria.

2. **Gatilhos de parada obrigatória** — se durante qualquer trabalho for detectada a
   necessidade de mudar uma ferramenta/abordagem por um destes motivos:
   - melhorar a **segurança operacional**;
   - melhorar a **blindagem contra invasão (hackers)**;
   - melhorar a **velocidade de interação** com o usuário;
   - melhorar o **layout/UX**;
   - **qualquer outra melhoria** relevante detectada;
   → **NÃO seguir adiante por conta própria.** Parar, e levar a questão para
   **decisão conjunta** com o responsável (Levi).

3. **Decisão sempre conjunta.** O desenvolvedor (ou IA) **não adota inferências** nem
   decide sozinho mudanças estruturais. Deve **trazer vantagens e desvantagens** de
   cada opção e deixar a decisão com o responsável.

4. **Certeza de segurança.** Nenhuma solução é adotada sem certeza da sua segurança.
   Na dúvida, **testar primeiro** no ambiente de teste — mas a decisão final é sempre
   do responsável.

5. **Pós-decisão.** Somente **após a decisão conjunta**: atualizar TODA a documentação
   (este manual + manual do usuário), definir **sprints**, **planejamento de execução**
   e registrar **lições aprendidas**.

### 14.1 Fluxo de sprints

- Toda evolução é planejada em **sprints** com escopo fechado.
- Cada sprint segue: **planejar → implementar em `develop` → testar em TESTE →
  promover para `main` (PROD) → revisar este manual + o Manual do Usuário.**
- Ao final de cada sprint, **atualizar a Seção 15 (Histórico) e a 16 (Lições)**.
- Nenhum sprint é considerado concluído sem testes e sem revisão dos dois manuais.

---

## 15. Histórico de mudanças

> Registro do que está em vigência e do que foi alterado/descontinuado.

| Data | Mudança | Status |
|---|---|---|
| 2026 | Primeira versão do app (motor + UI + memorial) | ✅ Em operação |
| 2026 | Auth via `st.secrets` formato inline table | ❌ Descontinuado (quebrava no Cloud) |
| 2026 | Auth via seções paralelas `[auth_hashes]/...` | ✅ Em operação |
| 2026 | Roles admin/user + Painel Admin | ✅ Em operação |
| 2026 | Base NG: extração via PDF (5.404 munic., com erros) | ❌ Substituído |
| 2026 | Base NG: planilha oficial ABNT (5.571 munic.) | ✅ Em operação |
| 2026 | E-mails `.eml` em quoted-printable | ❌ Substituído (caracteres quebrados) |
| 2026 | E-mails `.eml` em base64 | ✅ Em operação |
| 2026 | Ícone de raio (PNG/ICO) | ✅ Em operação |
| 2026 | Manifest PWA customizado (injeção via JS) | ⚠️ Não confirmado (ver Lições) |
| 01/05/2026 | **Decisão:** migrar hospedagem Streamlit Cloud → Railway (2 ambientes) | 🟡 Em implantação (Sprint 0) |
| 01/05/2026 | Config Railway: `railway.json`, `start.sh`, `.python-version` | 🟡 Em implantação |
| 01/05/2026 | **Decisão:** domínio de produção `pda.tesconsult.com.br` | 🟡 Em implantação |
| 01/05/2026 | Branch `develop` criada para o ambiente de teste | 🟡 Em implantação |

---

## 16. Lições aprendidas

> Erros reais encontrados no desenvolvimento e suas soluções. **Ler antes de mexer
> em autenticação, deploy ou e-mails.**

### L1 — `hashlib.compare_digest` quebra com `st.secrets`
- **Sintoma:** `AttributeError` no login em produção (funcionava local).
- **Causa:** o Streamlit Cloud envolve valores de `st.secrets` em wrappers internos
  que não são `str`/`bytes` puros; `compare_digest` exige tipos estritos.
- **Solução:** função `_coerce_str()` força conversão para string pura e comparação
  com `==` direto. Para hashes PBKDF2 em app interno, `==` é seguro o suficiente.

### L2 — TOML inline tables quebram no Streamlit Cloud
- **Sintoma:** `AttributeError` ao ler `{ hash="...", expira="..." }`.
- **Causa:** o parser de Secrets do Cloud embrulha o inline table de forma incompatível.
- **Solução:** usar seções paralelas (`[auth_hashes]`, `[auth_expira]`, `[auth_roles]`),
  cada uma `email = "valor"` string simples.

### L3 — E-mails `.eml` com texto corrompido
- **Sintoma:** palavras quebradas com `=` no meio (`par= Análise`, `c=lular`).
- **Causa:** o módulo `email` do Python usa quoted-printable por padrão, que insere
  "soft line breaks" (`=` no fim de linha) a cada 76 caracteres; alguns Outlook não
  decodificam isso.
- **Solução:** `msg.set_content(corpo, charset="utf-8", cte="base64")` + `policy=SMTP`.

### L4 — Base NG extraída de PDF estava incompleta e com erros
- **Sintoma:** ~85 municípios faltando e alguns com UF trocada (ex.: Xanxerê SC→PR).
- **Causa:** extração de texto de tabela multi-coluna de PDF é não-confiável.
- **Solução:** usar a **planilha oficial ABNT** (.xlsx), não o PDF. 5.571 municípios.

### L5 — Subdomínio Streamlit bloqueado por "profanidade"
- **Sintoma:** `pda-analise-risco` rejeitado ("contains profanity").
- **Causa:** filtro detecta a substring "anal" em "análise".
- **Solução:** usar nome sem essa substring (`pda-nbr5419-ar`, `calculadora-pda`).

### L6 — Acentuação em caminho de arquivo (`PADRÕES`) corrompe `.url`
- **Sintoma:** atalho `.url` no desktop não achava o ícone (caminho com `Õ`).
- **Causa:** encoding ASCII do `.url` não lida com o caractere acentuado do caminho.
- **Solução:** copiar o ícone para um caminho sem acento (`%LOCALAPPDATA%\VertecSPDA\`).

### L7 — Streamlit read-only impede self-service de senha
- **Sintoma:** não há como o usuário trocar a própria senha sem o admin.
- **Causa:** `st.secrets` é somente-leitura em runtime.
- **Solução (planejada):** migrar usuários para PostgreSQL (Railway). Ver Sprint 1.

### L8 — Windows quebra acentuação no terminal
- **Sintoma:** `UnicodeEncodeError` ao rodar scripts com emojis/acentos.
- **Solução:** sempre `set PYTHONUTF8=1` (CMD) ou `$env:PYTHONUTF8="1"` (PowerShell).

---

## 17. Roadmap

| Prioridade | Item | Sprint |
|---|---|---|
| Alta | Separação Teste/Produção + branches | Sprint 0 |
| Alta | Banco PostgreSQL (Railway) p/ usuários | Sprint 1 |
| Alta | Self-service de troca de senha + "Minha conta" | Sprint 2 |
| Média | Log de auditoria (quem fez o quê) | Sprint 3 |
| Média | Salvar/carregar projetos do usuário | Sprint 4 |
| Média | Frequência de danos F (Seção 7) na UI | A definir |
| Média | Anexo D (R4) completo com ca/cb/cc/cs | A definir |
| Baixa | Tornar repositório privado (fase comercial) | A definir |
| Baixa | Testes automatizados vs. exemplos da norma | A definir |
| Baixa | Cobrança (Stripe/Asaas) + expiração automática | Fase comercial |

---

*Fim do Manual do Desenvolvedor. Mantenha-o vivo: revise ao final de cada sprint.*
