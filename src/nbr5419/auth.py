"""Autenticação por email + senha para o app Streamlit.

Senhas são armazenadas como hashes PBKDF2-SHA256 (100k iterações, salt = email).
O segredo (lista de usuários autorizados) fica em st.secrets, configurado via
Streamlit Cloud Settings → Secrets, e nunca vai ao GitHub.

Formato recomendado (seções paralelas, mais robusto):

    [auth_hashes]
    "eng03@vertecenergia.com" = "<hash_pbkdf2>"

    [auth_expira]
    "eng03@vertecenergia.com" = "2099-12-31"

Use scripts/gerar_hash.py para gerar hashes.
Use scripts/gerenciar_acessos.py para revogar/renovar.
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

    return ResultadoAuth("OK", email=email_norm, expira=expira)


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
        st.caption(
            "Acesso restrito a projetistas autorizados. "
            "Para solicitar acesso, contate o administrador do sistema."
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

    st.sidebar.markdown("---")
    st.sidebar.caption(f"👤 **{usuario}**")

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
        st.rerun()
