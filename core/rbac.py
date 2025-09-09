from __future__ import annotations
from typing import Set
from sqlalchemy import select
from .db import SessionLocal
from .models import Role, Permission, User

DEFAULT_PERMISSIONS: list[tuple[str, str]] = [
    # usuários
    ("users.view",   "Visualizar lista de usuários"),
    ("users.create", "Criar usuários"),
    ("users.update", "Editar usuários"),
    ("users.delete", "Excluir usuários"),
    # clientes
    ("clients.view_all",   "Ver todos os clientes"),
    ("clients.view_own",   "Ver apenas clientes próprios"),
    ("clients.create",     "Cadastrar clientes"),
    ("clients.update_all", "Editar qualquer cliente"),
    ("clients.update_own", "Editar clientes próprios"),
    ("clients.delete_all", "Excluir qualquer cliente"),
    ("clients.delete_own", "Excluir clientes próprios"),
    ("clients.assign_responsible", "Atribuir responsável do cliente"),  # <- NOVA
]

ROLE_DEFAULT_PERMISSIONS: dict[str, list[str]] = {
    "admin": ["*"],
    "recepcao": ["users.view", "clients.view_all", "clients.assign_responsible"],
    "estagiario": ["users.view"],
    "advogado": ["clients.create", "clients.view_own", "clients.update_own", "clients.delete_own"],
}

class RBACService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def get_or_create_permissions(self) -> list[Permission]:
        with self.session_factory() as db:
            existing = {p.name: p for p in db.scalars(select(Permission)).all()}
            changed = False
            for name, desc in DEFAULT_PERMISSIONS:
                if name not in existing:
                    db.add(Permission(name=name, description=desc))
                    changed = True
            if changed:
                db.commit()
            return db.scalars(select(Permission)).all()

    def assign_default_permissions_to_roles(self) -> None:
        with self.session_factory() as db:
            roles = {r.name: r for r in db.scalars(select(Role)).all()}
            perms_all = {p.name: p for p in db.scalars(select(Permission)).all()}
            for role_name, perm_names in ROLE_DEFAULT_PERMISSIONS.items():
                role = roles.get(role_name)
                if not role:
                    continue
                target = list(perms_all.values()) if "*" in perm_names else [perms_all[n] for n in perm_names if n in perms_all]
                current = {p.name for p in role.permissions}
                for p in target:
                    if p.name not in current:
                        role.permissions.append(p)
            db.commit()

    # (métodos sync_permissions / effective_permissions / can) — mantenha como estavam
    def effective_permissions(self, user: User) -> Set[str]:
        names: Set[str] = set()
        for role in user.roles:
            for p in role.permissions:
                names.add(p.name)
        return names

    def can(self, user: User, perm_name: str) -> bool:
        return perm_name in self.effective_permissions(user)
