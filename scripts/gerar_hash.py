"""Gera entrada de usuário (hash + expiração) para secrets.toml.

Uso:
    python scripts/gerar_hash.py

Pede e-mail, senha e data de expiração interativamente.
Imprime a linha pronta para colar no secrets.toml ou no painel
Streamlit Cloud > Settings > Secrets.
"""
import getpass
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nbr5419.auth import hash_senha


def main() -> None:
    print("=" * 65)
    print("Gerador de credenciais — Análise de Risco SPDA Vertec")
    print("=" * 65)

    email = input("E-mail (ex.: eng06@vertecenergia.com): ").strip()
    if not email or "@" not in email:
        print("[ERRO] E-mail inválido.")
        sys.exit(1)

    senha = getpass.getpass("Senha (não aparece na tela): ")
    if len(senha) < 6:
        print("[AVISO] Senha curta — recomenda-se mínimo 8 caracteres.")
    confirmacao = getpass.getpass("Confirmar senha: ")
    if senha != confirmacao:
        print("[ERRO] Senhas não conferem.")
        sys.exit(1)

    print()
    print("Data de expiração do acesso (ISO YYYY-MM-DD).")
    print("  - Validação/uso interno: 2099-12-31 (recomendado, acesso indeterminado)")
    print("  - Trial comercial:       use a data real (ex.: 2026-12-31)")
    expira_str = input("Data [2099-12-31]: ").strip() or "2099-12-31"

    try:
        expira = date.fromisoformat(expira_str)
    except ValueError:
        print(f"[ERRO] Data inválida: {expira_str}. Use formato YYYY-MM-DD.")
        sys.exit(1)

    if expira < date.today():
        print(f"[AVISO] Data de expiração ({expira}) é anterior a hoje. "
              "O usuário será bloqueado imediatamente.")

    h = hash_senha(email, senha)
    print()
    print("Adicione/atualize em secrets.toml ou Streamlit Cloud > Secrets:")
    print()
    print("[auth]")
    print(f'"{email}" = {{ hash = "{h}", expira = "{expira_str}" }}')
    print()


if __name__ == "__main__":
    main()
