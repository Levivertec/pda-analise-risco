"""Autenticação por email + senha + role para o app Streamlit.

Senhas são armazenadas como hashes PBKDF2-SHA256 (100k iterações, salt = email).
O segredo (lista de usuários autorizados) fica em st.secrets, configurado via
Streamlit Cloud Settings → Secrets, e nunca vai ao GitHub.

Formato recomendado (seções paralelas):

    [auth_hashes]
    "user@empresa.com" = "<hash_pbkdf2>"

    [auth_expira]
    "user@empresa.com" = "2099-12-31"

    [auth_roles]
    "user@empresa.com" = "admin"   # ou "user" (default)

    [auth_admin_emails]
    contato = "levi@vertecenergia.com,contato@tectos.com.br"

Use scripts/gerar_hash.py para gerar hashes.
Use scripts/gerenciar_acessos.py para revogar/renovar/promover.
"""
from __future__ import annotations

import hashlib
from datetime import date, datetime
from typing import NamedTuple

import streamlit as st


HASH_ITERATIONS = 100_000
DATA_INDETERMINADA = date(2099, 12, 31)


class ResultadoAuth(NamedTuple):
    """Resultado da verificação de credenciais."""
    status: str               # "OK" | "INEXISTENTE" | "SENHA_ERRADA" | "EXPIRADO"
    email: str = ""
    expira: date | None = None
    role: str = "user"        # "admin" | "user"


def hash_senha(email: str, senha: str) -> str:
    """Hash determinístico de senha. Salt = email (case-insensitive)."""
    salt = email.strip().lower().encode("utf-8")
    return hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt, HASH_ITERATIONS
    ).hex()


def _parse_data(valor) -> date:
    """Aceita string ISO (YYYY-MM-DD), datetime.date ou datetime.datetime."""
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        return date.fromisoformat(valor.strip())
    return DATA_INDETERMINADA


def _buscar_no_dict(d, email_norm: str):
    """Busca case-insensitive em st.secrets dict-like. Retorna valor ou None."""
    if d is None:
        return None
    try:
        for chave in d:
            if str(chave).strip().lower() == email_norm:
                return d[chave]
    except Exception:
        return None
    return None


def _verificar_credenciais(email: str, senha: str) -> ResultadoAuth:
    """Verifica email/senha/expiração contra st.secrets.

    Lê dois formatos:
    - Novo (recomendado): seções [auth_hashes] e [auth_expira]
    - Legado (compatível): seção [auth] com strings (sem expiração)
    """
    email_norm = email.strip().lower()
    hash_armazenado: str | None = None
    expira: date = DATA_INDETERMINADA

    # Formato novo (preferencial)
    if "auth_hashes" in st.secrets:
        valor = _buscar_no_dict(st.secrets["auth_hashes"], email_norm)
        if valor is not None:
            hash_armazenado = str(valor).strip()
        if "auth_expira" in st.secrets:
            data_v = _buscar_no_dict(st.secrets["auth_expira"], email_norm)
            if data_v is not None:
                try:
                    expira = _parse_data(str(data_v))
                except Exception:
                    expira = DATA_INDETERMINADA

    # Formato legado [auth] = string apenas
    if hash_armazenado is None and "auth" in st.secrets:
        valor = _buscar_no_dict(st.secrets["auth"], email_norm)
        if valor is not None and isinstance(valor, str):
            hash_armazenado = valor.strip()

    if hash_armazenado is None:
        return ResultadoAuth("INEXISTENTE")

    hash_calculado = hash_senha(email_norm, senha)
    if not hashlib.compare_digest(hash_calculado, hash_armazenado):
        return ResultadoAuth("SENHA_ERRADA")

    if expira < date.today():
        return ResultadoAuth("EXPIRADO", email=email_norm, expira=expira)

    # Lê role; default = "user"
    role = "user"
    if "auth_roles" in st.secrets:
        valor = _buscar_no_dict(st.secrets["auth_roles"], email_norm)
        if valor:
            role = str(valor).strip().lower()
            if role not in ("admin", "user"):
                role = "user"

    return ResultadoAuth("OK", email=email_norm, expira=expira, role=role)


def emails_admins() -> list[str]:
    """Retorna lista de e-mails dos administradores cadastrados.

    Útil para a tela de 'Solicitar acesso' montar o destinatário.
    """
    if "auth_roles" not in st.secrets:
        return []
    admins = []
    try:
        for email in st.secrets["auth_roles"]:
            if str(st.secrets["auth_roles"][email]).strip().lower() == "admin":
                admins.append(str(email))
    except Exception:
        pass
    return admins


def usuario_atual() -> dict | None:
    """Retorna {'email', 'role', 'expira'} do usuário logado, ou None."""
    email = st.session_state.get("usuario_autenticado")
    if not email:
        return None
    return {
        "email": email,
        "role": st.session_state.get("usuario_role", "user"),
        "expira": st.session_state.get("usuario_expira"),
    }


def is_admin() -> bool:
    """True se o usuário logado for admin."""
    return st.session_state.get("usuario_role") == "admin"


def _tela_login() -> None:
    """Renderiza a tela de login (single-column, centralizada)."""
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_esq, col_meio, col_dir = st.columns([1, 2, 1])
    with col_meio:
        st.markdown("# ⚡ Análise de Risco SPDA")
        st.caption("ABNT NBR 5419-2:2026 — Vertec Energia")
        st.markdown("---")

        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 🔐 Login")
            email = st.text_input(
                "E-mail corporativo",
                placeholder="seu.email@vertecenergia.com",
                autocomplete="email",
            )
            senha = st.text_input("Senha", type="password", autocomplete="current-password")
            col1, col2 = st.columns(2)
            with col1:
                entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)
            with col2:
                st.form_submit_button("Limpar", use_container_width=True)

        if entrar:
            if not email or not senha:
                st.error("Preencha email e senha.")
            else:
                resultado = _verificar_credenciais(email, senha)
                if resultado.status == "OK":
                    st.session_state["usuario_autenticado"] = resultado.email
                    st.session_state["usuario_expira"] = resultado.expira
                    st.session_state["usuario_role"] = resultado.role
                    st.rerun()
                elif resultado.status == "EXPIRADO":
                    st.error(
                        f"⏰ Seu acesso expirou em "
                        f"**{resultado.expira.strftime('%d/%m/%Y')}**. "
                        "Entre em contato com o administrador para renovação."
                    )
                else:  # INEXISTENTE ou SENHA_ERRADA — mensagem genérica por segurança
                    st.error("E-mail ou senha incorretos.")

        st.markdown("---")

        with st.expander("📨 Não tenho cadastro — solicitar acesso"):
            _formulario_solicitar_acesso()

        st.caption(
            "Acesso restrito a usuários autorizados pelo administrador. "
            "Solicitações de novos cadastros são revisadas manualmente."
        )


def _formulario_solicitar_acesso() -> None:
    """Formulário público que envia e-mail aos admins solicitando acesso."""
    import urllib.parse

    with st.form("solicitar_acesso", clear_on_submit=False):
        nome = st.text_input("Nome completo")
        email_solicitante = st.text_input(
            "E-mail corporativo",
            placeholder="seu.email@empresa.com",
        )
        empresa = st.text_input("Empresa/organização")
        justificativa = st.text_area(
            "Por que você precisa de acesso?",
            placeholder="Ex.: Engenheiro projetista de SPDA, vou usar para projetos da minha carteira.",
            max_chars=500,
        )
        enviar = st.form_submit_button("📧 Gerar pedido por e-mail", type="primary")

    if enviar:
        if not nome or not email_solicitante or not justificativa:
            st.error("Preencha nome, e-mail e justificativa.")
            return

        admins = emails_admins()
        if not admins:
            st.error(
                "Sem administradores configurados. Contate o suporte: "
                "levi@vertecenergia.com"
            )
            return

        assunto = f"[Análise de Risco SPDA] Solicitação de acesso — {nome}"
        corpo = (
            f"Solicitação de acesso ao app de Análise de Risco SPDA (NBR 5419-2):\n\n"
            f"Nome: {nome}\n"
            f"E-mail: {email_solicitante}\n"
            f"Empresa: {empresa or '(não informado)'}\n\n"
            f"Justificativa:\n{justificativa}\n\n"
            f"---\n"
            f"Para aprovar: rode 'python scripts/gerenciar_acessos.py' "
            f"e adicione o usuário."
        )
        mailto = (
            f"mailto:{','.join(admins)}"
            f"?subject={urllib.parse.quote(assunto)}"
            f"&body={urllib.parse.quote(corpo)}"
        )

        st.success(
            "✅ Solicitação preparada. Clique no botão abaixo para abrir seu "
            "cliente de e-mail e enviar aos administradores."
        )
        st.markdown(
            f'<a href="{mailto}" target="_blank">'
            f'<button style="background-color:#1f4e79;color:white;'
            f'padding:10px 20px;border:none;border-radius:5px;cursor:pointer;'
            f'font-size:14px;">📧 Enviar e-mail para administradores</button></a>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Após o envio, aguarde retorno dos administradores. "
            "Você receberá login e senha por canal seguro caso o pedido seja aprovado."
        )


def exigir_login() -> str:
    """Bloqueia o app até o usuário se autenticar.

    Retorna o email do usuário autenticado.
    Chame esta função no início de app.py, antes de qualquer outra coisa.
    """
    if "usuario_autenticado" in st.session_state:
        return st.session_state["usuario_autenticado"]

    _tela_login()
    st.stop()  # interrompe a execução até o próximo rerun com login válido


def botao_logout() -> None:
    """Mostra o usuário logado e botão de logout (use na sidebar)."""
    usuario = st.session_state.get("usuario_autenticado", "")
    if not usuario:
        return
    expira: date | None = st.session_state.get("usuario_expira")
    role = st.session_state.get("usuario_role", "user")

    st.sidebar.markdown("---")
    icone = "🛡️" if role == "admin" else "👤"
    role_label = "Administrador" if role == "admin" else "Usuário"
    st.sidebar.caption(f"{icone} **{usuario}**  \n_{role_label}_")

    # Aviso quando faltar pouco para expirar (≤ 30 dias e não-indeterminado)
    if expira and expira < DATA_INDETERMINADA:
        dias_restantes = (expira - date.today()).days
        if dias_restantes <= 30:
            st.sidebar.warning(
                f"⏰ Acesso expira em **{dias_restantes} dia(s)** "
                f"({expira.strftime('%d/%m/%Y')})"
            )
        elif dias_restantes <= 90:
            st.sidebar.caption(
                f"📅 Acesso válido até {expira.strftime('%d/%m/%Y')}"
            )

    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state.pop("usuario_autenticado", None)
        st.session_state.pop("usuario_expira", None)
        st.session_state.pop("usuario_role", None)
        st.rerun()
