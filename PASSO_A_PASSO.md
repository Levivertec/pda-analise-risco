# 📋 Passo-a-passo do ciclo de vida do produto

Da liberação para os 3 projetistas até a transição comercial — em 4 fases.

---

## 🎯 Fase 1 — Liberar para os projetistas (validação por tempo indeterminado)

**Objetivo:** Karol, Patrick e Larissa testam o app pelo tempo que precisarem,
sem nenhum prazo de corte.

### Pré-requisitos (uma vez só)

- [ ] Git instalado (`https://git-scm.com/download/win`)
- [ ] Conta GitHub criada
- [ ] Conta Streamlit Cloud criada (login com GitHub)

### Passo 1.1 — Subir o código no GitHub

Abra o **PowerShell** ou **CMD** na pasta do projeto:

```
cd "C:\Users\LeviCarvalho\vertecenergia.com\TES CONSULT - Documentos\04. PADRÕES\IA\AR 5419"
git init -b main
git add .
git commit -m "primeira versao"
git remote add origin https://github.com/SEU-USUARIO/vertec-spda.git
git push -u origin main
```

> ⚠️ **Confira no GitHub** depois do push: o arquivo `.streamlit/secrets.toml`
> **NÃO** deve estar lá (ele tem hashes de senhas). Se aparecer, alguma coisa
> deu errado no `.gitignore` — me avise.

### Passo 1.2 — Deploy no Streamlit Cloud

1. Vá em `https://share.streamlit.io` → **Create app** → **Deploy from GitHub**
2. Selecione o repositório `vertec-spda`, branch `main`, arquivo `app.py`
3. **App URL**: escolha `vertec-spda` → `https://vertec-spda.streamlit.app`
4. Em **Advanced settings → Secrets**, cole:

```toml
[auth]
"eng03@vertecenergia.com" = { hash = "df69eef9c064b3f14b845e8b468950108e8d516315f6c16abbfd2fc006538d9e", expira = "2099-12-31" }
"eng04@vertecenergia.com" = { hash = "d1309ae906b46002f1dfa5ade9ada62c5ae881d381127d8c089ebc8efab04ee2", expira = "2099-12-31" }
"eng05@vertecenergia.com" = { hash = "c8247a8fffe4dece80adccc32b25f782ab9ea521366f680cf4e804bd7642a435", expira = "2099-12-31" }
```

5. Clique em **Deploy**. Em ~3 minutos, o app está no ar.

### Passo 1.3 — Mandar os e-mails

```
python scripts/gerar_emails.py
```

Preencha as variáveis (URL real, seu nome, prazo de feedback). O script gera
3 arquivos `.eml` em `emails/`. Duplo-clique em cada um → Outlook abre →
revise → **Enviar**.

### Passo 1.4 — Mandar as senhas no Teams (separadamente)

| Para | Mensagem direta |
|---|---|
| Karol (eng03) | `Sua senha do app SPDA: 8BEHaxTcnJYz` |
| Patrick (eng04) | `Sua senha do app SPDA: VCN6R6vxdu3b` |
| Larissa (eng05) | `Sua senha do app SPDA: KBSbVvmKSbth` |

✅ **Pronto.** Os 3 projetistas têm acesso por tempo **indeterminado** (até
2099-12-31, na prática "para sempre"). Eles testam pelo tempo que precisarem.

---

## 🔄 Fase 2 — Manter durante a validação

### Atualizar o app com correções/melhorias

Você modifica o código localmente, testa com `streamlit run app.py`, e
publica:

```
deploy.bat "descricao da mudanca"
```

Streamlit Cloud detecta o push e reimplanta sozinho em 1-2 min.

### Conferir quem está usando

```
python scripts/gerenciar_acessos.py
```

Opção `[1] Listar`. Os 3 aparecem com status "ativo (indeterminado)".

### Receber feedback

Os projetistas mandam por e-mail/Teams. Recomenda-se anotar tudo num
arquivo `FEEDBACK.md` (não criado ainda) para priorizar correções.

### Adicionar mais um projetista (se precisar)

```
python scripts/gerenciar_acessos.py
# [2] Adicionar usuário
# email, senha, expira = 2099-12-31
# [7] Mostrar bloco TOML pronto
```

Copie o TOML que aparece e cole em **Streamlit Cloud → Settings → Secrets**.
Em ~30s o novo usuário consegue logar.

---

## 💰 Fase 3 — Transição validação → comercial

Dia que você decidir que o produto vai virar pago. Sugestão de prazo:
**~30 dias entre comunicar e bloquear**.

### Passo 3.1 — Avisar os projetistas

E-mail individual para Karol, Patrick e Larissa:

> "Pessoal, obrigado pela validação intensiva nesses últimos meses. A partir
> de **DD/MM/AAAA** o software entra em fase comercial — seu acesso atual
> será encerrado nessa data. Estaremos disponibilizando um modelo
> [individual / corporativo Vertec / etc.] caso queiram continuar usando."

### Passo 3.2 — Configurar a data de corte

```
python scripts/gerenciar_acessos.py
# [6] Migrar todos da validação para data fixa
# Nova data: 2026-06-30 (exemplo — ajuste para sua data)
```

Os 3 projetistas passam de "indeterminado" para "expira em DD/MM/AAAA".
Confirma com `s`.

### Passo 3.3 — Sincronizar com Streamlit Cloud

```
# Mesmo script, opção [7]
```

Copie o bloco TOML que aparece e cole em **Streamlit Cloud → Settings →
Secrets**. Salve.

A partir de agora, contam-se os dias até a expiração. Quando faltarem
≤ 30 dias, os projetistas verão um aviso amarelo na sidebar do app.

### Passo 3.4 — No dia do corte (automático)

Quando a data passar, na próxima tentativa de uso o projetista vê:

> ⏰ Seu acesso expirou em DD/MM/AAAA. Entre em contato com o
> administrador para renovação.

Não precisa fazer nada manual — é automático com base na data.

---

## 🚀 Fase 4 — Operação comercial

### Cadastrar um novo cliente pagante

Cliente paga (à vista, mensal, anual), você cadastra:

```
python scripts/gerenciar_acessos.py
# [2] Adicionar
# email = cliente@empresa.com.br
# senha = (gere uma forte; o cliente troca depois)
# expira = data fim do contrato (ex.: 2027-04-30 para 1 ano)
# [7] Mostrar TOML
```

Sincroniza com Streamlit Cloud, manda email + senha pro cliente
(separados, como você fez com os projetistas).

### Renovar assinatura de cliente que pagou

```
python scripts/gerenciar_acessos.py
# [4] Renovar
# Seleciona o cliente
# Nova data = data fim da nova assinatura
# [7] Sincroniza
```

### Cancelar acesso de cliente que não renovou

Duas opções:
- **[3] Revogar** — mantém cadastro, só põe data passada (fácil de renovar)
- **[5] Remover** — apaga completo (precisa recadastrar do zero)

Recomendação: **revogar** primeiro, **remover** só após 6 meses sem renovação.

---

## 🛡️ Boas práticas de operação

### Backup do secrets.toml local

O arquivo `.streamlit/secrets.toml` tem todos os hashes. **Faça backup** em
local seguro (cofre de senhas, OneDrive criptografado, etc.). Se você
perder esse arquivo, perde a fonte de verdade — a única outra cópia é o
que está em Streamlit Cloud Secrets, e lá não dá para baixar/exportar.

### Trocar senhas periodicamente

A cada 3-6 meses, especialmente:
- Após saída de algum projetista
- Após suspeita de vazamento
- No fim da validação, antes do comercial

### Auditar quem tem acesso

Mensalmente, rode `[1] Listar` e confira:
- Todos os ativos ainda devem estar lá?
- Algum cliente com data próxima de expirar?
- Algum cliente já expirado que pode ser removido?

### Quando suspeitar de vazamento

Se uma senha pode ter vazado (foi enviada por canal errado, projetista
saiu sem entregar credenciais, etc.):

1. **Imediato:** `[3] Revogar` o usuário e sincroniza com Streamlit Cloud
2. **Em seguida:** `[2] Adicionar` com nova senha forte
3. Comunique a pessoa correta pelo Teams com a senha nova

---

## 🆘 Troubleshooting comum

| Problema | Causa provável | Solução |
|---|---|---|
| Projetista diz "senha incorreta" | Streamlit Cloud Secrets não foi atualizado após mudança | Rode `[7]` e cole no painel |
| Todos foram bloqueados | TOML mal-formatado em Streamlit Cloud | Veja o histórico do Secrets, restaure versão anterior |
| App não atualiza após `git push` | Streamlit Cloud em cache | Force redeploy: app → ⋮ → "Reboot" |
| App lento na primeira requisição | Free tier dorme após inatividade | Normal, primeira req leva ~30s. Upgrade se incomodar |
| Quero ver erros do app | Logs em produção | Streamlit Cloud → app → "Manage app" (canto inf. dir.) |

---

## 📞 Suporte de emergência

Se algo crítico der errado e você precisa **bloquear acesso de TODOS imediatamente**:

1. Vá em https://share.streamlit.io
2. Seu app → **⋮ → Settings → Secrets**
3. **Apague todo o conteúdo** e clique Save
4. App reinicia em ~30s — ninguém mais consegue logar (vai dar erro genérico)

Para restaurar: cole de volta o conteúdo do seu backup do `secrets.toml`.

---

## 📚 Documentos relacionados

- [DEPLOY.md](DEPLOY.md) — Detalhes do primeiro deploy (mais técnico)
- [OPERACAO.md](OPERACAO.md) — Manual de operação dia-a-dia
- [README.md](README.md) — Visão geral técnica do projeto
