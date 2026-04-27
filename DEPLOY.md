# 🚀 Guia de Deploy — Streamlit Cloud

Passo-a-passo para colocar a aplicação no ar e liberar para os projetistas.

## Pré-requisitos (uma vez só)

1. **Git** — `https://git-scm.com/download/win` → Next, Next, Install (defaults estão OK)
2. **Conta GitHub** — `https://github.com/signup` (use seu e-mail Vertec)
3. **Conta Streamlit Cloud** — `https://share.streamlit.io` (faça login com GitHub)

---

## Etapa 1 — Criar repositório no GitHub

1. Acesse `https://github.com/new`
2. Configure:
   - **Repository name**: `vertec-spda-analise-risco`
   - **Description**: "Análise de Risco SPDA — ABNT NBR 5419-2:2026"
   - **Visibility**: ⚠️ **Public** *(privado também funciona, mas tem cota mensal de horas no Streamlit Cloud free)*
   - ❌ **NÃO** marque "Add a README" / .gitignore / license — já temos esses arquivos no projeto
3. Clique em **Create repository**
4. **Anote a URL** mostrada na próxima tela. Algo como:
   `https://github.com/seu-usuario/vertec-spda-analise-risco.git`

---

## Etapa 2 — Subir o código (CMD ou PowerShell, na pasta do projeto)

```bash
cd "C:\Users\LeviCarvalho\vertecenergia.com\TES CONSULT - Documentos\04. PADRÕES\IA\AR 5419"

git init -b main
git add .
git commit -m "primeira versao do app NBR 5419-2"
git remote add origin https://github.com/SEU-USUARIO/vertec-spda-analise-risco.git
git push -u origin main
```

⚠️ **Importante**: o `.gitignore` já está configurado para **NÃO** subir `.streamlit/secrets.toml` (que contém os hashes). Confirme depois do push olhando no GitHub que esse arquivo não está lá.

Na primeira vez o `git push` vai pedir login no GitHub — autorize via navegador.

---

## Etapa 3 — Deploy no Streamlit Cloud

1. Acesse `https://share.streamlit.io`
2. Clique em **"Create app"** → **"Deploy a public app from GitHub"**
3. Configure:
   - **Repository**: selecione `seu-usuario/vertec-spda-analise-risco`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: escolha algo como `vertec-spda` → fica `https://vertec-spda.streamlit.app`
4. Em **Advanced settings**:
   - **Python version**: `3.11`
5. **Antes de clicar em "Deploy"**, expanda **Secrets** e cole o conteúdo abaixo (TOML):

```toml
[auth]
"eng03@vertecenergia.com" = "df69eef9c064b3f14b845e8b468950108e8d516315f6c16abbfd2fc006538d9e"
"eng04@vertecenergia.com" = "d1309ae906b46002f1dfa5ade9ada62c5ae881d381127d8c089ebc8efab04ee2"
"eng05@vertecenergia.com" = "c8247a8fffe4dece80adccc32b25f782ab9ea521366f680cf4e804bd7642a435"
```

6. Clique em **Deploy**. Em ~3 minutos o app está no ar.

---

## Etapa 4 — Compartilhar com os projetistas

Para cada projetista, envie por **canal seguro** (Teams direct message, e-mail criptografado), separadamente:

| Projetista | Senha temporária |
|---|---|
| eng03@vertecenergia.com | *(consulte a mensagem original do Claude)* |
| eng04@vertecenergia.com | *(consulte a mensagem original do Claude)* |
| eng05@vertecenergia.com | *(consulte a mensagem original do Claude)* |

URL do app: `https://vertec-spda.streamlit.app` (ou a que você escolheu).

⚠️ **Não compartilhe a tabela completa em grupo público.** Mande cada senha separadamente para o projetista correspondente.

---

## Como adicionar/remover usuários depois

### Adicionar um novo projetista

1. Rode `python scripts/gerar_hash.py` localmente
2. Informe o email e uma senha forte
3. Copie a linha gerada (formato `"email" = "hash"`)
4. Vá em `https://share.streamlit.io` → seu app → **⋮ → Settings → Secrets**
5. Adicione a linha dentro de `[auth]` e clique **Save**
6. O app reinicia automaticamente em ~30s — não precisa fazer push novo

### Remover um projetista

Edite Secrets em Streamlit Cloud, apague a linha do email, salve.

### Trocar senha de um projetista

Mesma coisa: rode `gerar_hash.py`, substitua o valor no Secrets.

---

## Como atualizar o código depois

Quando você modificar o app localmente:

```bash
cd "C:\Users\LeviCarvalho\vertecenergia.com\TES CONSULT - Documentos\04. PADRÕES\IA\AR 5419"
git add .
git commit -m "descricao da mudanca"
git push
```

Streamlit Cloud detecta o push e atualiza em ~1-2 minutos. Os projetistas conectados precisam dar F5 para pegar a versão nova.

---

## Troubleshooting

**"git: command not found"** → instale Git no link acima e abra um terminal **novo**.

**Push pediu user/password e disse "support for password authentication was removed"** → use o GitHub CLI (`https://cli.github.com`) com `gh auth login`, ou crie um Personal Access Token em GitHub → Settings → Developer settings → Tokens.

**App no ar mas dá "Login: senha incorreta"** → confira em Streamlit Cloud → Secrets se o hash foi colado completo, sem espaços extras. Os hashes são longos (64 caracteres hex).

**Quero ver os logs** → no Streamlit Cloud, dentro do app, "Manage app" no canto inferior direito mostra logs em tempo real.

**App ficou lento ou caiu** → free tier dorme após inatividade. Primeira requisição demora ~30s. Para uso intenso, considere upgrade.
