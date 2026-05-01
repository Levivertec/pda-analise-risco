"""Gerenciador de acessos do app — CLI interativo.

Permite:
- Listar usuários atuais com status (ativo/expirado, role admin/user)
- Adicionar novo usuário (com role escolhível)
- Revogar acesso (define data de expiração no passado)
- Renovar acesso (define nova data de expiração)
- Remover usuário completamente
- Promover/rebaixar (admin <-> user)

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
    """Lê secrets.toml. Retorna {email: {hash, expira, role}}."""
    if not SECRETS_PATH.exists():
        return {}
    dados = tomllib.loads(SECRETS_PATH.read_text(encoding="utf-8"))
    hashes = dados.get("auth_hashes", {})
    expiras = dados.get("auth_expira", {})
    roles = dados.get("auth_roles", {})

    # Compatibilidade: formato legado [auth] com strings
    if not hashes and "auth" in dados:
        for email, valor in dados["auth"].items():
            if isinstance(valor, str):
                hashes[email] = valor

    resultado: dict[str, dict] = {}
    for email, hash_v in hashes.items():
        resultado[email] = {
            "hash": hash_v,
            "expira": expiras.get(email, DATA_INDETERMINADA),
            "role": (roles.get(email, "user") or "user").lower(),
        }
    return resultado


def salvar(usuarios: dict) -> None:
    """Reescreve .streamlit/secrets.toml em formato de seções paralelas."""
    SECRETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    linhas = [
        "# Credenciais de autenticação — NÃO COMMITAR",
        "# Configure os mesmos valores em Streamlit Cloud > Settings > Secrets",
        "",
        "[auth_hashes]",
    ]
    for email, info in sorted(usuarios.items()):
        linhas.append(f'"{email}" = "{info["hash"]}"')

    linhas.append("")
    linhas.append("[auth_expira]")
    for email, info in sorted(usuarios.items()):
        linhas.append(f'"{email}" = "{info["expira"]}"')

    linhas.append("")
    linhas.append("[auth_roles]")
    for email, info in sorted(usuarios.items()):
        linhas.append(f'"{email}" = "{info.get("role", "user")}"')

    linhas.append("")
    SECRETS_PATH.write_text("\n".join(linhas), encoding="utf-8")


def status_usuario(info: dict) -> tuple[str, str]:
    """Retorna (status_texto, cor_terminal_ANSI)."""
    try:
        exp = date.fromisoformat(info["expira"])
    except ValueError:
        return "INVALIDO", "\033[91m"

    hoje = date.today()
    if exp < hoje:
        return f"EXPIRADO em {exp.strftime('%d/%m/%Y')}", "\033[91m"
    if exp == date(2099, 12, 31):
        return "ativo (indeterminado)", "\033[92m"
    dias = (exp - hoje).days
    if dias <= 30:
        return f"ativo até {exp.strftime('%d/%m/%Y')} ({dias}d)", "\033[93m"
    return f"ativo até {exp.strftime('%d/%m/%Y')} ({dias}d)", "\033[92m"


def listar(usuarios: dict) -> None:
    if not usuarios:
        print("\n[!] Nenhum usuário cadastrado.\n")
        return
    print()
    print("=" * 90)
    print(f"{'#':<3} {'Role':<6} {'E-mail':<35} Status")
    print("-" * 90)
    for i, (email, info) in enumerate(sorted(usuarios.items()), 1):
        status_txt, cor = status_usuario(info)
        reset = "\033[0m"
        role = info.get("role", "user")
        role_marca = "[A]" if role == "admin" else "[U]"
        print(f"{i:<3} {role_marca:<6} {email:<35} {cor}{status_txt}{reset}")
    print("=" * 90)
    print("Legenda: [A] = administrador, [U] = usuário comum\n")


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

    role = input("Role [user/admin] (padrão: user): ").strip().lower() or "user"
    if role not in ("user", "admin"):
        print("[AVISO] Role inválido, assumindo 'user'.")
        role = "user"

    usuarios[email] = {
        "hash": hash_senha(email, senha),
        "expira": expira,
        "role": role,
    }
    salvar(usuarios)
    print(f"[OK] {email} adicionado como {role}, expira {expira}.")
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
    print("\n>>> Aplique também em Streamlit Cloud > Secrets.\n")


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


def promover(usuarios: dict) -> None:
    print("\n--- Promover/rebaixar (admin <-> user) ---")
    email = escolher_usuario(usuarios, "promover/rebaixar")
    if not email:
        return
    atual = usuarios[email].get("role", "user")
    novo = "user" if atual == "admin" else "admin"
    print(f"Role atual: {atual} -> novo: {novo}")
    confirma = input("Confirmar? (s/N): ").strip().lower()
    if confirma != "s":
        print("Cancelado.")
        return
    usuarios[email]["role"] = novo
    salvar(usuarios)
    print(f"[OK] {email} agora é '{novo}'.")
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
        if info["expira"] == DATA_INDETERMINADA and info.get("role", "user") != "admin"
    ]
    if not afetados:
        print("[!] Nenhum usuário 'user' com acesso indeterminado encontrado.")
        return
    print(f"\nUsuários a serem migrados ({len(afetados)}, admins preservados):")
    for e in afetados:
        print(f"  - {e}")
    if input("Confirma? (s/N): ").strip().lower() != "s":
        print("Cancelado.")
        return
    for email in afetados:
        usuarios[email]["expira"] = nova
    salvar(usuarios)
    print(f"\n[OK] {len(afetados)} usuário(s) migrados para expirar em {nova}.")
    print("Admins mantidos com acesso indeterminado.")
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
    print("[6] Promover/rebaixar (admin <-> user)")
    print("[7] Migrar todos da validação para data fixa")
    print("[8] Mostrar bloco TOML pronto para colar no Streamlit Cloud")
    print("[0] Sair")


def mostrar_toml(usuarios: dict) -> None:
    if not usuarios:
        print("\n[!] Sem usuários.\n")
        return
    print("\nCole isto em Streamlit Cloud > Settings > Secrets:")
    print("-" * 65)
    print("[auth_hashes]")
    for email, info in sorted(usuarios.items()):
        print(f'"{email}" = "{info["hash"]}"')
    print()
    print("[auth_expira]")
    for email, info in sorted(usuarios.items()):
        print(f'"{email}" = "{info["expira"]}"')
    print()
    print("[auth_roles]")
    for email, info in sorted(usuarios.items()):
        print(f'"{email}" = "{info.get("role", "user")}"')
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
            promover(usuarios)
        elif op == "7":
            expirar_todos_validacao(usuarios)
        elif op == "8":
            mostrar_toml(usuarios)
        elif op == "0":
            print("Até logo.")
            return
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
