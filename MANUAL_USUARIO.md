# 📘 Manual do Usuário — Calculadora PDA

### Análise de Risco SPDA conforme ABNT NBR 5419-2:2026

> **Para quem é este manual:** engenheiros e técnicos projetistas de SPDA. Você **não
> precisa saber programar** para usar o aplicativo. Este guia mostra o passo a passo,
> com dicas, para você fazer uma análise de risco completa com tranquilidade.
>
> *Versão esboço 1.0 — 01/05/2026. Uma versão ilustrada/diagramada será produzida
> futuramente. As marcações `[ILUSTRAÇÃO: ...]` indicam onde entrarão imagens.*

---

## Índice

1. [O que é a Calculadora PDA](#1-o-que-é-a-calculadora-pda)
2. [Como acessar](#2-como-acessar)
3. [Primeiro acesso e senha](#3-primeiro-acesso-e-senha)
4. [Visão geral da tela](#4-visão-geral-da-tela)
5. [Passo a passo da análise](#5-passo-a-passo-da-análise)
6. [Entendendo os resultados](#6-entendendo-os-resultados)
7. [Gerando o memorial](#7-gerando-o-memorial)
8. [Perguntas frequentes](#8-perguntas-frequentes)
9. [Glossário rápido](#9-glossário-rápido)
10. [Suporte](#10-suporte)

---

## 1. O que é a Calculadora PDA

A Calculadora PDA faz a **análise de risco** exigida pela norma **ABNT NBR 5419-2:2026**
para projetos de Proteção contra Descargas Atmosféricas (SPDA).

Você informa os dados da estrutura (dimensões, localização, medidas de proteção,
linhas conectadas) e o aplicativo calcula automaticamente:

- **R1** — Risco de perda de **vida humana**
- **R3** — Risco de perda de **patrimônio cultural** (quando aplicável)
- **R4** — Risco de perda de **valor econômico** (opcional)

Ao final, compara os riscos calculados com os **riscos toleráveis** da norma e diz se
a estrutura **precisa ou não de proteção** — e gera um **memorial de cálculo** pronto
para anexar ao seu projeto.

---

## 2. Como acessar

1. Abra o navegador (recomendado: **Google Chrome** ou **Microsoft Edge**)
2. Acesse o endereço do aplicativo (enviado a você pela equipe)
3. Aparecerá a tela de **login**

> 💡 **Dica:** salve o endereço nos favoritos ou instale como aplicativo (no Chrome/Edge:
> menu → "Instalar página como app") para abrir com um clique, como um programa.

[ILUSTRAÇÃO: tela de login com campos E-mail e Senha]

---

## 3. Primeiro acesso e senha

- **Login:** seu e-mail corporativo (ex.: `seu.nome@empresa.com`)
- **Senha:** enviada separadamente pela equipe (por mensagem direta, não por e-mail)

### Não tem cadastro?
Na tela de login, clique em **"📨 Não tenho cadastro — solicitar acesso"**, preencha o
formulário, e sua solicitação será encaminhada aos administradores.

[ILUSTRAÇÃO: formulário "Solicitar acesso"]

> 🔒 **Segurança:** não compartilhe seu login e senha com outras pessoas. Cada acesso
> é individual.

---

## 4. Visão geral da tela

Depois de entrar, a tela tem duas áreas:

- **Menu lateral (esquerda):** as etapas da análise, numeradas de 1 a 6, mais o
  Glossário. No rodapé, aparece seu nome e o botão **Sair**.
- **Área principal (centro):** onde você preenche os dados de cada etapa.

[ILUSTRAÇÃO: visão geral com menu lateral destacado]

> 💡 As etapas funcionam como um assistente: preencha na ordem (1 → 6). Você pode voltar
> a qualquer etapa clicando no menu.

---

## 5. Passo a passo da análise

### Etapa 1 — Localização e NG
Selecione a **UF** e o **município** da obra. O aplicativo preenche automaticamente o
valor de **NG** (densidade de descargas atmosféricas) conforme o Anexo F da norma.

> 💡 O NG vem da tabela oficial da ABNT. Você não precisa procurar em lugar nenhum —
> basta escolher a cidade.

[ILUSTRAÇÃO: seleção de UF/município e o NG preenchido]

### Etapa 2 — Estrutura
Informe as **dimensões** (comprimento, largura, altura), o **tipo de construção** e a
**localização relativa** (se há prédios vizinhos mais altos, se está isolada etc.).

> 💡 Passe o mouse sobre o ícone **(?)** ao lado de cada campo para ver a explicação
> e a referência da norma.
>
> 💡 Se sua estrutura tem formato irregular e você já calculou a **área de exposição
> (Ae/AD)** por método gráfico, pode informá-la manualmente marcando a opção
> correspondente.

[ILUSTRAÇÃO: campos de dimensões e área de exposição]

### Etapa 3 — Zonas de estudo
Divida a estrutura em **zonas** com características parecidas (mesmo tipo de piso,
mesma compartimentação). Para projetos simples, **uma única zona já basta**.

Em cada zona, informe: número de pessoas, tempo de permanência, tipo de piso, risco
de incêndio/explosão, medidas contra incêndio e características dos sistemas internos.

> 💡 Use mais de uma zona apenas quando partes da estrutura forem realmente diferentes
> (ex.: área administrativa × galpão industrial no mesmo edifício).

[ILUSTRAÇÃO: cartão de uma zona expandido]

### Etapa 4 — Linhas conectadas
Cadastre as **linhas que entram na estrutura** (energia e sinal/dados). São a principal
porta de entrada de surtos. Informe tipo, comprimento, instalação (aérea/enterrada),
ambiente e blindagem.

> 💡 Se a estrutura é isolada (sem linhas externas), pode seguir sem cadastrar nenhuma.

[ILUSTRAÇÃO: cartão de uma linha]

### Etapa 5 — Medidas de proteção
Informe o **nível do SPDA** (ou se não há), o **sistema de DPS** e medidas adicionais
contra tensão de toque/passo.

> 💡 Esta é a etapa que você mais vai "mexer" para simular: experimente diferentes
> níveis de proteção e veja, na Etapa 6, qual combinação deixa o risco aceitável.

[ILUSTRAÇÃO: seleção de nível de SPDA e DPS]

### Etapa 6 — Resultados
O aplicativo mostra os riscos calculados (R1, R3, R4) comparados com os toleráveis,
com indicação visual (🟢 aceitável / 🔴 precisa de proteção), gráficos e diagnóstico.

[ILUSTRAÇÃO: dashboard de resultados com indicadores]

---

## 6. Entendendo os resultados

- **🟢 Verde (R ≤ RT):** o risco está dentro do tolerável. A estrutura atende à norma
  com as medidas informadas.
- **🔴 Vermelho (R > RT):** o risco está acima do tolerável. São necessárias medidas
  de proteção adicionais (volte à Etapa 5 e simule).

O painel mostra também **qual componente** (RA, RB, RV...) mais contribui para o risco —
isso indica **onde investir** em proteção para ser mais eficiente.

> 💡 Exemplo: se o componente RV (danos pela linha de energia) é o maior, instalar DPS
> classe I na entrada costuma ser a medida mais efetiva.

---

## 7. Gerando o memorial

Na Etapa 6, ao final, há três botões:

- **📕 Baixar PDF** — para anexar ao projeto / entregar ao cliente
- **📘 Baixar Word** — caso precise editar
- **📝 Baixar Markdown** — formato texto simples

O memorial traz todos os dados de entrada, áreas, eventos, medidas, componentes por
zona e a conclusão (risco vs. tolerável).

[ILUSTRAÇÃO: três botões de download e exemplo de memorial em PDF]

> 💡 Confira sempre o memorial antes de entregar. A responsabilidade técnica final
> (ART) é do profissional projetista.

---

## 8. Perguntas frequentes

**O aplicativo substitui o meu julgamento de engenharia?**
Não. Ele automatiza os cálculos da norma, mas a interpretação de zonas, fatores e
medidas, e a responsabilidade técnica, são suas.

**Posso usar no celular?**
Funciona, mas a experiência é melhor no computador (telas e tabelas maiores).

**Esqueci minha senha. E agora?**
No momento, contate o administrador. *(Em breve haverá troca de senha self-service.)*

**Meus dados ficam salvos?**
No momento, cada análise é feita na hora. Baixe o memorial ao terminar.
*(Salvar projetos está no roadmap.)*

**O NG que aparece está diferente do que eu esperava.**
O valor vem da tabela oficial da ABNT (Anexo F). A norma exige usar exatamente esse valor.

---

## 9. Glossário rápido

| Termo | Significado |
|---|---|
| **SPDA** | Sistema de Proteção contra Descargas Atmosféricas |
| **NG** | Densidade de descargas atmosféricas (raios/km²/ano) |
| **R1** | Risco de perda de vida humana |
| **R3** | Risco de perda de patrimônio cultural |
| **R4** | Risco de perda de valor econômico |
| **RT** | Risco tolerável (limite da norma) |
| **DPS** | Dispositivo de Proteção contra Surtos |
| **NP** | Nível de Proteção do SPDA (I a IV; I é o mais rigoroso) |
| **Zona de estudo** | Parte da estrutura com características homogêneas |
| **Memorial** | Documento com os cálculos e a conclusão da análise |

---

## 10. Suporte

Dúvidas, erros ou sugestões durante o uso: contate a equipe pelos canais informados
no seu convite de acesso (e-mail / Teams / WhatsApp).

> 💬 Seu retorno é importante: relate qualquer cálculo que pareça incorreto, campo
> confuso ou ideia de melhoria.

---

*Fim do Manual do Usuário (esboço). Versão ilustrada/diagramada será produzida sob demanda.*
