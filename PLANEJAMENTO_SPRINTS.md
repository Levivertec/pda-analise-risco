# 🗺️ Planejamento de Sprints — Calculadora PDA

> Plano de execução acordado em **decisão conjunta** (01/05/2026). Todos os itens
> recomendados na auditoria foram aprovados. Cada sprint segue a
> [Regra de Ouro](MANUAL_DESENVOLVEDOR.md#140-premissas-de-governança-regra-de-ouro):
> nasce em **teste** (branch `develop`), é validado, e só então promovido para
> **produção** (branch `main`). Ao fim de cada sprint: testes → segurança →
> revisão dos manuais.

**Legenda:** 🔵 Planejado · 🟡 Em andamento · ✅ Concluído

---

## Sprint 0 — Fundação de ambientes 🟡

**Objetivo:** dois ambientes (teste e produção) idênticos, robustos, no Railway, com
app reproduzível e código protegido.

| Item | Descrição | Status |
|---|---|---|
| C1 | Migrar hospedagem para Railway (projeto `calculadora-pda`) | 🟡 |
| — | Branches `main` (prod) e `develop` (teste) | ✅ |
| — | Config Railway (`railway.json`, `start.sh`, `.python-version`, `.gitattributes`) | ✅ |
| — | Ambiente **production** no Railway (app + PostgreSQL) | 🔵 aguardando |
| — | Ambiente **test** no Railway (app + PostgreSQL) | 🔵 |
| — | Domínio `pda.tesconsult.com.br` (produção) | 🔵 |
| — | Migrar projetistas para o ambiente de teste do Railway | 🔵 |
| E1 | **Travar versões** das dependências (`==`) p/ reprodutibilidade | 🔵 |
| B1 | **Tornar repositório privado** | 🔵 ⚠️ ver risco de ordem |

> ⚠️ **Risco de ordem (B1):** tornar o repositório privado **antes** de migrar os
> projetistas para o Railway pode **derrubar o app atual no Streamlit Cloud** (free tier
> tem limite para repositório privado), interrompendo a validação. **Decisão:** o B1 só
> deve ser executado **depois** que os projetistas estiverem no Railway e o app antigo
> do Streamlit Cloud puder ser aposentado.

**Critério de saída:** teste e produção no ar no Railway, login OK nos dois, domínio
ativo, versões travadas, repo privado (após migração), Streamlit Cloud aposentado.

---

## Sprint 1 — Segurança de autenticação 🔵

**Objetivo:** base de usuários robusta e auditável no banco.

| Item | Descrição |
|---|---|
| A2 | Migrar autenticação de env var → **PostgreSQL** (com fallback durante transição) |
| B3 | Restaurar comparação segura de hash (`hmac.compare_digest` com `_coerce_str`) |
| A1 | **Rotacionar todas as senhas** (as atuais estão em texto plano no histórico) |

**Critério de saída:** login lendo do banco em teste e produção; senhas novas
distribuídas; comparação de hash à prova de *timing attack*.

---

## Sprint 2 — Self-service e blindagem 🔵

| Item | Descrição |
|---|---|
| — | Página **"Minha conta"** com troca de senha self-service |
| — | Regras de senha (10+ caracteres, maiúscula, minúscula, número, especial, medidor) |
| B2 | **Bloqueio anti-força-bruta** (após N tentativas falhas) |
| B4 | **Salt aleatório por usuário** (substitui salt = e-mail) |

**Critério de saída:** usuário troca a própria senha sem admin; conta bloqueia após
tentativas; hashes com salt individual.

---

## Sprint 3 — Auditoria e qualidade 🔵

| Item | Descrição |
|---|---|
| A3 | **Log de auditoria** (login, troca de senha, criação/revogação de usuário) |
| E2 | **Testes automatizados** do motor vs. exemplos da norma |
| E3 | **CI** (rodar testes automaticamente a cada push) |

**Critério de saída:** auditoria consultável no painel admin; testes cobrindo os 8
componentes; CI verde bloqueando merge com teste quebrado.

---

## Sprint 4 — Performance e UX 🔵

| Item | Descrição |
|---|---|
| C2 | **Cache** de cálculos pesados (resposta mais rápida) |
| D1 | **Ícone próprio** no app/favicon |
| P-001 | Resolver ícone/nome do **PWA** (ver PENDENCIAS.md) |

**Critério de saída:** app perceptivelmente mais rápido; identidade visual consistente.

---

## Sprint 5 — Manutenibilidade 🔵

| Item | Descrição |
|---|---|
| D2 | **Refatorar `app.py`** (1.327 linhas) em múltiplas páginas/módulos |

> Pré-requisito: Sprint 3 concluído (testes automatizados) para detectar regressões.

**Critério de saída:** `app.py` modular, navegação por páginas, sem regressão.

---

## Backlog futuro / fase comercial 🔵

| Item | Descrição |
|---|---|
| B5 | **2FA** (autenticação em dois fatores) para admins |
| — | Cobrança (Stripe/Asaas) + expiração automática de assinatura |
| — | Salvar/carregar projetos do usuário |
| — | **Frequência de danos F** (Seção 7) na UI |
| — | **R4 / Anexo D** completo (ca/cb/cc/cs por zona) |

---

## Fluxo de execução de cada sprint

1. Criar branch `feature/...` a partir de `develop`.
2. Implementar + testar localmente.
3. Merge em `develop` → deploy automático no **ambiente de teste** (Railway).
4. Validar exaustivamente em teste.
5. **Decisão conjunta** de promover.
6. PR `develop` → `main` → deploy automático em **produção**.
7. Revisar `MANUAL_DESENVOLVEDOR.md`, `MANUAL_USUARIO.md`, `PENDENCIAS.md` e este plano.
8. Registrar lições aprendidas.
