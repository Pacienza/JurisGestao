import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.rbac import RBACService  # noqa: E402
from core.auth import AuthService  # noqa: E402

def main():
    p = argparse.ArgumentParser(description="RBAC: permissões & seed")
    p.add_argument("--seed", action="store_true", help="Cria permissões padrão e atribui aos papéis padrão")
    p.add_argument("--list", action="store_true", help="Lista permissões de cada papel")
    args = p.parse_args()

    auth = AuthService()
    rbac = RBACService()

    if args.seed:
        auth.get_or_create_roles()
        rbac.get_or_create_permissions()
        rbac.assign_default_permissions_to_roles()
        print("RBAC seed aplicado.")

    if args.list:
        with auth.session_factory() as db:
            from sqlalchemy import select
            from core.models import Role
            roles = db.scalars(select(Role)).all()
            for role in roles:
                perms = ", ".join(sorted(p.name for p in role.permissions))
                print(f"- {role.name}: {perms or '(sem permissões)'}")

if __name__ == "__main__":
    main()
