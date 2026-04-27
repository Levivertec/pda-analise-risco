"""Gerenciador de acessos do app — CLI interativo.

Permite:
- Listar usuários atuais com status (ativo/expirado/expira em breve)
- Adicionar novo usuário (hash + expiração)
- Revogar acesso (define data de expiração no passado)
- Renovar acesso (define nova data de expiração)
- Remover usuário completamente

Lê e atualiza .streamlit/secrets.toml. Para aplicar em produção, copie
o conteúdo atualizado para Streamlit Cloud > Settings > Secrets.

Uso:
    python scripts/gerenciar_acessos.py
"""
from __future__ import annotations

import getpass
import sys
from datetime import date, timedelta
from pathlib import Path

# Python 3.11+ tem tomllib nativo; em versões anteriores cai para tomli
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        print("[ERRO] Sem leitor TOML disponível. Atualize para Python 3.11+.")
        sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nbr5419.auth import hash_senha


SECRETS_PATH = Path(__file__).parent.parent / ".streamlit" / "secrets.toml"
DATA_INDETERMINADA = "2099-12-31"


def carregar() -> dict:
    """Lê secrets.toml. Retorna {email: {hash, expira}}."""
    if not SECRETS_PATH.exists():
        return {}
    dados = tomllib.loads(SECRETS_PATH.read_text(encoding="utf-8"))
    auth = dados.get("auth", {})
    # Normaliza para sempre ser {email: {hash, expira}}
    resultado: dict[str, dict] = {}
    for email, valor in auth.items():
        if isinstance(valor, str):
            resultado[email] = {"hash": valor, "expira": DATA_INDETERMINADA}
        else:
            resultado[email] = {
                "hash": valor.get("hash", ""),
                "expira": valor.get("expira", DATA_INDETERMINADA),
            }
    return resultado


def salvar(usuarios: dict) -> None:
    """Reescreve .streamlit/secrets.toml com a estrutura nova."""
    SECRETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    linhas = [
        "# Credenciais de autenticação — NÃO COMMITAR",
        "# Configure os mesmos valores em Streamlit Cloud > Settings > Secrets",
        "",
        "[auth]",
    ]
    for email, info in sorted(usuarios.items()):
        linhas.append(
            f'"{email}" = {{ hash = "{info["hash"]}", expira = "{info["expira"]}" }}'
        )
    linhas.append("")
    SECRETS_PATH.write_text("\n".join(linhas), encoding="utf-8")


def status_usuario(info: dict) -> tuple[str, str]:
    """Retorna (status_texto, cor_terminal_ANSI)."""
    try:
        exp = date.fromisoformat(info["expira"])
    except ValueError:
        return "INVALIDO", "\033[91m"  # vermelho

    hoje = date.today()
    if exp < hoje:
        return f"EXPIRADO em {exp.strftime('%d/%m/%Y')}", "\033[91m"  # vermelho
    if exp == date(2099, 12, 31):
        return "ativo (indeterminado)", "\033[92m"  # verde
    dias = (exp - hoje).days
    if dias <= 30:
        return f"ativo até {exp.strftime('%d/%m/%Y')} ({dias}d restantes)", "\033[93m"  # amarelo
    return f"ativo até {exp.strftime('%d/%m/%Y')} ({dias}d restantes)", "\033[92m"


def listar(usuarios: dict) -> None:
    if not usuarios:
        print("\n[!] Nenhum usuário cadastrado.\n")
        return
    print()
    print("=" * 80)
    print(f"{'#':<3} {'E-mail':<35} Status")
    print("-" * 80)
    for i, (email, info) in enumerate(sorted(usuarios.items()), 1):
        status_txt, cor = status_usuario(info)
        reset = "\033[0m"
        print(f"{i:<3} {email:<35} {cor}{status_txt}{reset}")
    print("=" * 80)
    print()


def escolher_usuario(usuarios: dict, acao: str) -> str | None:
    if not usuarios:
        print("[!] Nenhum usuário cadastrado.")
        return None
    listar(usuarios)
    emails = list(sorted(usuarios.keys()))
    while True:
        sel = input(f"Número do usuário para {acao} (vazio cancela): ").strip()
        if not sel:
            return None
        try:
            idx = int(sel) - 1
            if 0 <= idx < len(emails):
                return emails[idx]
        except ValueError:
            pass
        print("Entrada inválida.")


def adicionar(usuarios: dict) -> None:
    print("\n--- Adicionar novo usuário ---")
    email = input("E-mail: ").strip().lower()
    if not email or "@" not in email:
        print("[ERRO] E-mail inválido.")
        return
    if email in usuarios:
        print(f"[ERRO] {email} já existe. Use 'renovar' ou 'remover' antes.")
        return

    senha = getpass.getpass("Senha: ")
    if len(senha) < 6:
        print("[AVISO] Senha curta.")
    if senha != getpass.getpass("Confirmar senha: "):
        print("[ERRO] Senhas não conferem.")
        return

    expira = input(f"Expira em [{DATA_INDETERMINADA}]: ").strip() or DATA_INDETERMINADA
    try:
        date.fromisoformat(expira)
    except ValueError:
        print("[ERRO] Data inválida (use YYYY-MM-DD).")
        return

    usuarios[email] = {"hash": hash_senha(email, senha), "expira": expira}
    salvar(usuarios)
    print(f"[OK] {email} adicionado, expira {expira}.")
    print("\n>>> Lembre-se de aplicar o mesmo em Streamlit Cloud > Secrets.\n")


def revogar(usuarios: dict) -> None:
    print("\n--- Revogar acesso (define expiração para ontem) ---")
    email = escolher_usuario(usuarios, "revogar")
    if not email:
        return
    confirma = input(f"Revogar acesso de {email}? (s/N): ").strip().lower()
    if confirma != "s":
        print("Cancelado.")
        return
    ontem = (date.today() - timedelta(days=1)).isoformat()
    usuarios[email]["expira"] = ontem
    salvar(usuarios)
    print(f"[OK] Acesso de {email} revogado (expira {ontem}).")
    print("\n>>> Aplique também em Streamlit Cloud > Secrets para revogar em produção.\n")


def renovar(usuarios: dict) -> None:
    print("\n--- Renovar acesso (estender data de expiração) ---")
    email = escolher_usuario(usuarios, "renovar")
    if not email:
        return
    print(f"Expiração atual: {usuarios[email]['expira']}")
    nova = input(f"Nova data de expiração [{DATA_INDETERMINADA}]: ").strip() or DATA_INDETERMINADA
    try:
        date.fromisoformat(nova)
    except ValueError:
        print("[ERRO] Data inválida.")
        return
    usuarios[email]["expira"] = nova
    salvar(usuarios)
    print(f"[OK] Acesso de {email} renovado até {nova}.")
    print("\n>>> Aplique também em Streamlit Cloud > Secrets.\n")


def remover(usuarios: dict) -> None:
    print("\n--- Remover usuário (apaga completamente) ---")
    email = escolher_usuario(usuarios, "remover")
    if not email:
        return
    confirma = input(f"Remover {email} PERMANENTEMENTE? (s/N): ").strip().lower()
    if confirma != "s":
        print("Cancelado.")
        return
    del usuarios[email]
    salvar(usuarios)
    print(f"[OK] {email} removido.")
    print("\n>>> Aplique também em Streamlit Cloud > Secrets.\n")


def expirar_todos_validacao(usuarios: dict) -> None:
    """Atalho: define expiração para todos com data > 2099 (validação)
    para uma data específica. Útil na transição validação -> comercial."""
    print("\n--- Migrar todos os usuários de validação para data fixa ---")
    print("(Aplica apenas a usuários com expira = 2099-12-31)")
    nova = input("Nova data de expiração para validação (ex.: 2026-06-30): ").strip()
    if not nova:
        print("Cancelado.")
        return
    try:
        date.fromisoformat(nova)
    except ValueError:
        print("[ERRO] Data inválida.")
        return
    afetados = [
        email for email, info in usuarios.items()
        if info["expira"] == DATA_INDETERMINADA
    ]
    if not afetados:
        print("[!] Nenhum usuário com acesso indeterminado encontrado.")
        return
    print(f"\nUsuários a serem migrados ({len(afetados)}):")
    for e in afetados:
        print(f"  - {e}")
    if input("Confirma? (s/N): ").strip().lower() != "s":
        print("Cancelado.")
        return
    for email in afetados:
        usuarios[email]["expira"] = nova
    salvar(usuarios)
    print(f"\n[OK] {len(afetados)} usuário(s) migrados para expirar em {nova}.")
    print("\n>>> Aplique também em Streamlit Cloud > Secrets.\n")


def menu() -> None:
    print("\n" + "=" * 65)
    print("GERENCIADOR DE ACESSOS — Análise de Risco SPDA Vertec")
    print("=" * 65)
    print("[1] Listar usuários e status")
    print("[2] Adicionar usuário")
    print("[3] Revogar acesso (expirar ontem)")
    print("[4] Renovar acesso (estender data)")
    print("[5] Remover usuário (apagar)")
    print("[6] Migrar todos da validação para data fixa")
    print("[7] Mostrar bloco TOML pronto para colar no Streamlit Cloud")
    print("[0] Sair")


def mostrar_toml(usuarios: dict) -> None:
    if not usuarios:
        print("\n[!] Sem usuários.\n")
        return
    print("\nCole isto em Streamlit Cloud > Settings > Secrets:")
    print("-" * 65)
    print("[auth]")
    for email, info in sorted(usuarios.items()):
        print(f'"{email}" = {{ hash = "{info["hash"]}", expira = "{info["expira"]}" }}')
    print("-" * 65 + "\n")


def main() -> None:
    while True:
        usuarios = carregar()
        menu()
        op = input("Opção: ").strip()
        if op == "1":
            listar(usuarios)
        elif op == "2":
            adicionar(usuarios)
        elif op == "3":
            revogar(usuarios)
        elif op == "4":
            renovar(usuarios)
        elif op == "5":
            remover(usuarios)
        elif op == "6":
            expirar_todos_validacao(usuarios)
        elif op == "7":
            mostrar_toml(usuarios)
        elif op == "0":
            print("Até logo.")
            return
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
