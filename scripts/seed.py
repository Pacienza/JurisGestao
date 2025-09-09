import argparse
import sys
from pathlib import Path

# permite rodar tanto "python -m scripts.seed" quanto "python scripts/seed.py"
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.auth import AuthService  # noqa: E402

def main():
    parser = argparse.ArgumentParser(description="Seed/Reset do banco (desenvolvimento)")
    parser.add_argument("--reset", action="store_true", help="Drop e recria o schema (DADOS SERÃO PERDIDOS)")
    parser.add_argument("--seed", action="store_true", help="Cria roles e um usuário para cada role")
    parser.add_argument("--list", action="store_true", help="Lista usuários")
    args = parser.parse_args()

    auth = AuthService()
    if args.reset:
        auth.reset_database()
        print("Banco recriado (drop_all + create_all).")

    auth.create_schema_if_needed()

    if args.seed:
        auth.get_or_create_roles()
        created = auth.seed_one_actor_per_role()
        if created:
            print("Usuários criados:", created)
        else:
            print("Nenhum usuário criado (já existiam).")

    if args.list:
        users = auth.list_users()
        if not users:
            print("Nenhum usuário encontrado.")
        else:
            print("Usuários:")
            for uid, uname, email, active in users:
                print(f" - [{uid}] {uname} <{email}> ativo={active}")

        

if __name__ == "__main__":
    main()


"""
# reset total + seed + listar
python scripts/seed.py --reset --seed --list

# apenas seed (sem reset)
python scripts/seed.py --seed

# só listar
python scripts/seed.py --list

"""

