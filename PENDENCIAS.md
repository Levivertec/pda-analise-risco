# 📌 Lista de Pendências — Calculadora PDA

> Itens detectados que **não bloqueiam** o uso atual, registrados para tratamento
> futuro. Toda pendência deve ser tratada conforme a [Regra de Ouro de governança]
> (MANUAL_DESENVOLVEDOR.md, Seção 14.0): nasce no ambiente de **teste**, com decisão
> conjunta antes de ir para produção.

**Legenda de status:** 🔵 Aberta · 🟡 Em análise · 🟢 Decidida (aguardando sprint) · ✅ Concluída

---

## Pendências abertas

| ID | Item | Categoria | Status | Observações |
|----|------|-----------|--------|-------------|
| P-001 | **Ícone PWA personalizado** — ao instalar o app como aplicativo (PWA), o ícone e o nome aparecem como "streamlit" em vez do raio/Calculadora PDA. Há uma tentativa de correção **não commitada** no `app.py` (injeção de manifest via JS) que **não foi confirmada**. | Layout/UX | 🔵 Aberta | Não afeta produção (Railway puxa do GitHub, que tem a versão com emoji ⚡). Reavaliar após migração ao Railway — talvez o domínio próprio + config do Railway resolva de forma mais limpa. |

---

## Como uma pendência vira sprint

1. Pendência é discutida → **decisão conjunta** (vantagens/desvantagens).
2. Se aprovada, sai desta lista e entra no **planejamento de sprints**
   (MANUAL_DESENVOLVEDOR.md, Seção 17 — Roadmap).
3. Implementação em **teste** → validação → produção.
4. Ao concluir, marcar ✅ aqui e registrar em **Lições Aprendidas** se houver aprendizado.

---

*Demais melhorias detectadas na auditoria (segurança, blindagem, velocidade, qualidade)
estão no backlog de decisões e, uma vez aprovadas, viram sprints no Roadmap.*
