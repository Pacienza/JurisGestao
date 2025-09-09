from __future__ import annotations
from typing import Iterable, Set
from sqlalchemy import select
from .db import SessionLocal
from .models import Role, Permission, User

# Permissões padrão do sistema (primeiro módulo: usuários)
DEFAULT_PERMISSIONS: list[tuple[str, str]] = [
    ("users.view",   "Visualizar lista de usuários"),
    ("users.create", "Criar usuários"),
    ("users.update", "Editar usuários"),
    ("users.delete", "Excluir usuários"),
]

# Mapa de permissões por papel (seed inicial)
# Obs.: 'admin' recebe todas as permissões conhecidas.
ROLE_DEFAULT_PERMISSIONS: dict[str, list[str]] = {
    "admin": ["*"],                 # todas
    "recepcao": ["users.view"],     # leitura
    "estagiario": ["users.view"],   # leitura
    "advogado": [],                 # nenhuma sobre usuários
}

class RBACService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    # --- CRUD de permissões (interno/seed) ---
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
        """Atribui permissões padrão por papel conforme ROLE_DEFAULT_PERMISSIONS."""
        with self.session_factory() as db:
            roles = {r.name: r for r in db.scalars(select(Role)).all()}
            perms_all = {p.name: p for p in db.scalars(select(Permission)).all()}
            for role_name, perm_names in ROLE_DEFAULT_PERMISSIONS.items():
                role = roles.get(role_name)
                if not role:
                    continue
                if "*" in perm_names:
                    target_perms = list(perms_all.values())
                else:
                    target_perms = [perms_all[n] for n in perm_names if n in perms_all]
                # evita duplicidade
                current = {p.name for p in role.permissions}
                for p in target_perms:
                    if p.name not in current:
                        role.permissions.append(p)
                # não removemos permissões já existentes (idempotente)
            db.commit()

    # --- efetivo / checagem ---
    def effective_permissions(self, user: User) -> Set[str]:
        """Retorna o conjunto de permissões efetivas pelo(s) papel(is) do usuário."""
        names: set[str] = set()
        for role in user.roles:
            for p in role.permissions:
                names.add(p.name)
        return names

    def can(self, user: User, perm_name: str) -> bool:
        return perm_name in self.effective_permissions(user)
