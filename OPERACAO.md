# 🛠️ Manual de Operação — Análise de Risco SPDA

Este documento cobre o **dia-a-dia** depois que o app está no ar:
gestão de acessos, transição validação→comercial, manutenção.

> Para o **deploy inicial** (subir o app no ar pela primeira vez), siga o
> [DEPLOY.md](DEPLOY.md).

---

## 📅 Fases do produto

| Fase | Quem usa | Expiração | Onde gerenciar |
|---|---|---|---|
| **Validação** *(atual)* | Karol, Patrick, Larissa | `2099-12-31` (indeterminado) | Manual via CLI |
| **Trial comercial** | Cliente em teste pago | Data fim do trial | CLI por usuário |
| **Comercial pleno** | Clientes pagantes | Final da assinatura | CLI ou painel admin futuro |

---

## 🔐 Fase 1 — Validação (situação atual)

Os 3 projetistas têm acesso com `expira = "2099-12-31"`, ou seja, **acesso indeterminado**. Eles podem usar o app pelo tempo que precisarem, sem nenhuma data de corte.

### Como verificar quem está ativo agora

```
python scripts/gerenciar_acessos.py
```

Escolha opção `[1] Listar usuários e status`. Saída exemplo:

```
#   E-mail                              Status
1   eng03@vertecenergia.com             ativo (indeterminado)
2   eng04@vertecenergia.com             ativo (indeterminado)
3   eng05@vertecenergia.com             ativo (indeterminado)
```

### Adicionar mais um projetista durante a validação

```
python scripts/gerenciar_acessos.py
# Escolha [2] Adicionar usuário
# Informe email, senha, expira = 2099-12-31
```

O script atualiza `.streamlit/secrets.toml` localmente. **Você ainda precisa
sincronizar com o Streamlit Cloud** (próxima seção).

### Sincronizar com Streamlit Cloud

Toda alteração local precisa ser refletida em produção. Caminho:

1. Rode `python scripts/gerenciar_acessos.py`, opção `[7] Mostrar bloco TOML`
2. Copie tudo que aparece (do `[auth]` até a última linha)
3. Vá em https://share.streamlit.io → seu app → **⋮ → Settings → Secrets**
4. Substitua o conteúdo lá pela cópia, clique **Save**
5. App reinicia em ~30s, novo acesso ativo

---

## 💰 Fase 2 — Transição para comercial (futuro)

Quando você decidir que a validação acabou e o produto vai virar pago, o
processo recomendado é:

### Passo 1 — Comunicar antecipadamente os projetistas da validação

E-mail/mensagem ~30 dias antes do corte: "obrigado pela validação, a partir
de DD/MM/AAAA o software entra em fase comercial e seu acesso atual será
encerrado. Novo modelo: [explicar plano comercial]."

### Passo 2 — Definir uma data de corte

```
python scripts/gerenciar_acessos.py
# Escolha [6] Migrar todos da validação para data fixa
# Informe data: 2026-06-30 (exemplo)
```

Isso muda automaticamente a expiração de **todos** os usuários com
`2099-12-31` para a data informada. Os 3 projetistas continuam com acesso
até essa data, depois são bloqueados na próxima tentativa de login.

### Passo 3 — Sincronizar com Streamlit Cloud

Mesma coisa de antes: opção `[7]` → copiar TOML → colar em Secrets.

### Passo 4 — Cadastrar primeiros clientes pagantes

Para cada cliente:

```
python scripts/gerenciar_acessos.py
# [2] Adicionar usuário
# email = cliente@empresa.com.br
# senha = (gerada e enviada ao cliente)
# expira = data fim do contrato (ex.: 2027-04-30 = 1 ano)
```

E sincroniza com Streamlit Cloud.

---

## 🚨 Operações de emergência

### Revogar acesso de um usuário AGORA (sem espera)

```
python scripts/gerenciar_acessos.py
# [3] Revogar acesso
# Escolhe o número do usuário
# Confirma com 's'
```

A expiração é definida para **ontem** — o usuário será bloqueado na próxima
ação dele dentro do app (ou no próximo login). **Você ainda precisa
sincronizar com Streamlit Cloud** (passo da seção anterior) para revogar em
produção.

### Renovar acesso de um cliente cuja assinatura foi paga

```
python scripts/gerenciar_acessos.py
# [4] Renovar acesso
# Escolhe o número
# Nova data: ex. 2027-04-30
```

### Remover completamente um usuário

```
python scripts/gerenciar_acessos.py
# [5] Remover usuário
```

Diferença entre *revogar* e *remover*:
- **Revogar**: mantém o registro, só muda a data — fácil de renovar depois
- **Remover**: apaga o usuário, precisa recadastrar do zero se voltar

---

## 🔑 Trocar senhas (recomendação periódica)

A boa prática é trocar senhas a cada 3-6 meses, especialmente após:
- Saída de funcionário
- Suspeita de vazamento
- Final de fase de validação (antes do comercial)

Para trocar a senha de um usuário:

```
python scripts/gerenciar_acessos.py
# [5] Remover (apaga o atual)
# [2] Adicionar (recria com nova senha)
```

Ou, mais direto: rode `python scripts/gerar_hash.py`, gere o novo hash,
edite manualmente o `secrets.toml` e o Streamlit Cloud Secrets.

---

## 📊 Status por cor (na CLI)

| Cor | Significado |
|---|---|
| 🟢 Verde | Acesso ativo (indeterminado ou > 30 dias para expirar) |
| 🟡 Amarelo | Acesso ativo mas expira em ≤ 30 dias |
| 🔴 Vermelho | Acesso expirado |

Os 3 projetistas atuais aparecerão sempre em verde durante a validação.

---

## 🆘 Fluxo se algo der errado

| Sintoma | Possível causa | Solução |
|---|---|---|
| Projetista diz "senha incorreta" mas você sabe que está certa | Hash não foi sincronizado com Streamlit Cloud | Refaça o passo de Sincronizar |
| Todos foram bloqueados de uma vez | Você editou Secrets e quebrou o TOML | Volte versão anterior (Streamlit Cloud guarda histórico) |
| Mensagem "Seu acesso expirou" | Data passou ou alguém revogou | Use opção [4] Renovar |
| App ficou totalmente sem auth | Removeu seção `[auth]` do Secrets | Adicione de volta `[auth]` com pelo menos 1 usuário |

---

## 📝 Checklist semanal recomendado (durante validação)

- [ ] Rodar `python scripts/gerenciar_acessos.py [1]` para ver status
- [ ] Conferir feedback recebido dos projetistas
- [ ] Aplicar pequenos ajustes no app (`deploy.bat "ajuste X"`)
- [ ] Confirmar que o app está respondendo (abrir a URL)

---

## 🔮 Quando o produto crescer

Este sistema baseado em arquivo TOML escala bem até ~50-100 usuários.
Acima disso, considere migrar para:

- **Banco de dados** (SQLite local ou Postgres na nuvem)
- **Painel admin web** dentro do próprio app (página `/admin` para gestão visual)
- **Stripe / Asaas** integrado para cobrança automática
- **Microsoft Entra ID** (SSO) para clientes corporativos

Mas isso é problema do amanhã. Por enquanto, o TOML + CLI atende.
