"""Gera arquivos .eml para envio aos projetistas em validação.

Pede informações interativamente e cria 3 arquivos em ./emails/.
Cada arquivo abre no Outlook com duplo-clique, com tudo pré-preenchido.

Uso:
    python scripts/gerar_emails.py
"""
from __future__ import annotations

import os
from email import policy
from email.message import EmailMessage
from pathlib import Path


PROJETISTAS = [
    {"id": "eng03", "nome": "Karol",   "email": "eng03@vertecenergia.com"},
    {"id": "eng04", "nome": "Patrick", "email": "eng04@vertecenergia.com"},
    {"id": "eng05", "nome": "Larissa", "email": "eng05@vertecenergia.com"},
]

ASSUNTO = "Convite para validação do software de Análise de Risco SPDA — NBR 5419-2"


CORPO_TEMPLATE = """Olá, {nome},

Espero que esteja bem.

Estamos em fase final de desenvolvimento de um software interno da Vertec para Análise de Risco SPDA conforme a ABNT NBR 5419-2:2026, e você foi selecionado para participar do grupo restrito de validação. A escolha levou em conta sua experiência técnica e o volume de projetos de SPDA que você atende — o seu retorno é fundamental para amadurecermos a ferramenta antes de qualquer disponibilização ampliada.

SOBRE A FERRAMENTA

O sistema cobre integralmente a Parte 2 da norma, calculando R1, R3, R4 e a frequência de danos F (Seção 7), com base de NG por município (Anexo F) e geração de memorial em PDF/Word.

COMO ACESSAR

1. URL do sistema: {url}
2. Login: {email}
3. Senha: enviarei separadamente por mensagem direta no Teams. Por questão de segurança, ela não vai por este e-mail.

Recomendo abrir pelo Chrome ou Edge, em computador. Funciona também no celular, mas a experiência é melhor no desktop.

COMO PARTICIPAR DA VALIDAÇÃO

1. Use a ferramenta em projetos reais ou cenários típicos do seu dia a dia.
2. Compare os resultados com seus cálculos atuais (planilha, software anterior, memoriais existentes).
3. Anote divergências, dúvidas, campos confusos, sugestões de melhoria.
4. Me retorne o feedback até {prazo}, por e-mail ou Teams. Pode ser texto livre, lista, prints — o que for mais prático.

Sugestão de pontos a observar:
- Os valores de R1, R3, F estão coerentes com cálculos manuais?
- Os campos do wizard estão claros? Faltou alguma opção?
- O memorial em PDF/Word está adequado para entrega ao cliente?
- Algum termo da norma ficou confuso ou ambíguo na interface?

CONFIDENCIALIDADE — LEIA COM ATENÇÃO

Este software é uma ferramenta interna proprietária da Vertec Energia, em desenvolvimento e de uso pessoal exclusivo dos projetistas designados. Por se tratar de versão pré-lançamento, peço três compromissos:

- Não compartilhar o link, login, senha ou prints do sistema com colegas, clientes ou terceiros — nem internamente fora deste grupo de validação.
- Não repassar o acesso para outras pessoas (mesmo da Vertec) sem autorização prévia minha.
- Não publicar capturas de tela em redes sociais, grupos públicos, fóruns ou apresentações externas.

Quando o software estiver maduro, faremos o lançamento oficial para toda a equipe técnica — neste momento, porém, o acesso é restrito a você, {outros_projetistas}.

SUPORTE DURANTE A VALIDAÇÃO

Qualquer dúvida, problema técnico ou sugestão, fale comigo diretamente:
{contato}

Conto com você. O feedback de quem usa a norma na ponta vai fazer toda a diferença para entregarmos uma ferramenta realmente útil.

Atenciosamente,
{remetente_nome}
{remetente_cargo}
Vertec Energia
"""


def perguntar(pergunta: str, default: str = "") -> str:
    sufixo = f" [{default}]" if default else ""
    resp = input(f"{pergunta}{sufixo}: ").strip()
    return resp if resp else default


def main() -> None:
    print("=" * 70)
    print("Gerador de e-mails — Validação Análise de Risco SPDA Vertec")
    print("=" * 70)
    print()
    print("Preencha as informações abaixo (Enter aceita o valor padrão entre []):")
    print()

    url = perguntar(
        "URL do app no ar (após deploy no Streamlit Cloud)",
        "https://vertec-spda.streamlit.app",
    )
    if "streamlit.app" not in url and "localhost" not in url:
        print("[AVISO] URL não parece ser do Streamlit Cloud. Confira antes de enviar.")

    remetente_nome = perguntar("Seu nome completo (remetente)")
    if not remetente_nome:
        print("[ERRO] Nome do remetente é obrigatório.")
        return

    remetente_cargo = perguntar("Seu cargo")
    remetente_email = perguntar("Seu e-mail Vertec (para campo De)")

    prazo = perguntar("Prazo para feedback (ex.: 15/05/2026)")
    if not prazo:
        print("[ERRO] Prazo é obrigatório.")
        return

    print("\nContato para suporte (3 linhas, deixe em branco para pular):")
    contato_email = perguntar("  E-mail")
    contato_teams = perguntar("  Teams")
    contato_telefone = perguntar("  Telefone/WhatsApp (opcional)")

    contato_linhas = []
    if contato_email:
        contato_linhas.append(f"- E-mail: {contato_email}")
    if contato_teams:
        contato_linhas.append(f"- Teams: {contato_teams}")
    if contato_telefone:
        contato_linhas.append(f"- Telefone/WhatsApp: {contato_telefone}")
    contato = "\n".join(contato_linhas) if contato_linhas else "- Pelos canais habituais"

    pasta_saida = Path(__file__).parent.parent / "emails"
    pasta_saida.mkdir(exist_ok=True)

    print()
    print("Gerando arquivos...")
    for proj in PROJETISTAS:
        outros = [p["nome"] for p in PROJETISTAS if p["id"] != proj["id"]]
        outros_str = " e ".join([", ".join(outros[:-1]), outros[-1]] if len(outros) > 1 else outros)

        corpo = CORPO_TEMPLATE.format(
            nome=proj["nome"],
            url=url,
            email=proj["email"],
            prazo=prazo,
            outros_projetistas=outros_str,
            contato=contato,
            remetente_nome=remetente_nome,
            remetente_cargo=remetente_cargo,
        )

        # policy=SMTP garante CRLF e RFC 5322 corretos
        # cte="base64" evita quebra de linha "= softbreak" do quoted-printable,
        # que renderiza incorretamente em alguns clientes Outlook
        msg = EmailMessage(policy=policy.SMTP)
        msg["Subject"] = ASSUNTO
        msg["To"] = proj["email"]
        if remetente_email:
            msg["From"] = remetente_email
        msg.set_content(corpo, subtype="plain", charset="utf-8", cte="base64")

        arquivo = pasta_saida / f"{proj['nome']}.eml"
        arquivo.write_bytes(bytes(msg))
        print(f"  [OK] {arquivo.name}  ->  {proj['email']}")

    print()
    print("=" * 70)
    print("Como enviar:")
    print("=" * 70)
    print(f"1. Abra a pasta: {pasta_saida}")
    print("2. Dê DUPLO-CLIQUE em cada arquivo .eml")
    print("3. O Outlook abre o e-mail pré-preenchido — revise e clique em Enviar")
    print()
    print("Lembrete: a SENHA de cada projetista deve ser enviada SEPARADAMENTE")
    print("por mensagem direta no Teams (NÃO inclua no e-mail).")
    print()


if __name__ == "__main__":
    main()
