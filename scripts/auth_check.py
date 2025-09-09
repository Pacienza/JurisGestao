import argparse
import sys
from pathlib import Path

# permite rodar tanto "python -m scripts.auth_check" quanto "python scripts/auth_check.py"
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.auth import AuthService  # noqa: E402

def main():
    p = argparse.ArgumentParser(description="Checar autenticação")
    p.add_argument("user", help="username ou email")
    p.add_argument("password", help="senha")
    args = p.parse_args()

    auth = AuthService()
    auth.create_schema_if_needed()
    account = auth.authenticate(args.user, args.password)
    if account:
        roles = [r.name for r in account.roles]
        print(f"Login OK: {account.username} | roles={roles}")
    else:
        print("Login inválido")

if __name__ == "__main__":
    main()
