from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .db import SessionLocal, engine
from .models import Base, User, Role
from .security import hash_password, verify_password
from .rbac import RBACService

DEFAULT_ROLES = [
    ("admin", "Administrador do sistema"),
    ("advogado", "Usuário advogado com acesso à própria agenda e clientes"),
    ("recepcao", "Atendimento/recepção, agenda e triagem"),
    ("estagiario", "Apoio com permissões restritas"),
]

class AuthService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
        self.rbac = RBACService(session_factory)

    # --- schema ---
    @staticmethod
    def create_schema_if_needed() -> None:
        Base.metadata.create_all(bind=engine)

    def reset_database(self) -> None:
        """DEV ONLY: drop_all + create_all."""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    # --- roles ---
    def get_or_create_roles(self) -> list[Role]:
        with self.session_factory() as db:
            roles = {r.name: r for r in db.scalars(select(Role)).all()}
            changed = False
            for name, desc in DEFAULT_ROLES:
                if name not in roles:
                    db.add(Role(name=name, description=desc))
                    changed = True
            if changed:
                db.commit()
            return db.scalars(select(Role).order_by(Role.name)).all()

    def list_roles(self) -> list[Role]:
        with self.session_factory() as db:
            return db.scalars(select(Role).order_by(Role.name)).all()

    # --- users ---
    def create_user(self, username: str, email: str, password: str, roles: list[str]) -> User:
        with self.session_factory() as db:
            role_objs = db.scalars(select(Role).where(Role.name.in_(roles))).all()
            user = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                roles=list(role_objs),
            )
            db.add(user)
            try:
                db.commit()
            except IntegrityError as e:
                db.rollback()
                raise ValueError(f"Usuário ou email já existe: {e}")
            db.refresh(user)
            return user

    def authenticate(self, username_or_email: str, password: str) -> Optional[User]:
        with self.session_factory() as db:
            stmt = select(User).where(
                (User.username == username_or_email) | (User.email == username_or_email)
            )
            user = db.scalars(stmt).first()
            if not user or not user.is_active:
                return None
            if verify_password(password, user.password_hash):
                return user
            return None

    def list_users(self) -> list[tuple[int, str, str, bool]]:
        """[(id, username, email, is_active), ...] — evita carregar papéis aqui."""
        with self.session_factory() as db:
            rows = db.execute(select(User.id, User.username, User.email, User.is_active)
                              .order_by(User.id)).all()
            return [(r[0], r[1], r[2], r[3]) for r in rows]

    def get_user(self, user_id: int) -> Optional[User]:
        with self.session_factory() as db:
            return db.get(User, user_id)

    def update_user(
        self, user_id: int, *, username: Optional[str]=None, email: Optional[str]=None,
        password: Optional[str]=None, is_active: Optional[bool]=None,
        roles: Optional[list[str]]=None
    ) -> User:
        with self.session_factory() as db:
            u = db.get(User, user_id)
            if not u:
                raise ValueError("Usuário não encontrado")
            if username is not None:
                u.username = username
            if email is not None:
                u.email = email
            if is_active is not None:
                u.is_active = is_active
            if password:
                u.password_hash = hash_password(password)
            if roles is not None:
                role_objs = db.scalars(select(Role).where(Role.name.in_(roles))).all()
                u.roles = list(role_objs)
            try:
                db.commit()
            except IntegrityError as e:
                db.rollback()
                raise ValueError(f"Conflito de unicidade: {e}")
            db.refresh(u)
            return u

    def delete_user(self, user_id: int) -> None:
        with self.session_factory() as db:
            u = db.get(User, user_id)
            if not u:
                return
            db.delete(u)
            db.commit()

    # --- seed ---
    def seed_one_actor_per_role(self) -> dict[str, str]:
        """Cria 1 usuário por role, se ainda não existir. Retorna {username: role}."""
        created: dict[str, str] = {}
        self.get_or_create_roles()
        defaults = [
            ("admin", "admin@local", "admin", ["admin"]),
            ("advogada", "advogada@local", "advogada", ["advogado"]),
            ("recepcao", "recepcao@local", "recepcao", ["recepcao"]),
            ("estagiario", "estagiario@local", "estagiario", ["estagiario"]),
        ]
        with self.session_factory() as db:
            for username, email, pwd, roles in defaults:
                exists = db.scalars(select(User).where(User.username == username)).first()
                if exists:
                    continue
                role_objs = db.scalars(select(Role).where(Role.name.in_(roles))).all()
                u = User(username=username, email=email,
                        password_hash=hash_password(pwd), roles=list(role_objs))
                db.add(u)
                created[username] = roles[0]
            db.commit()
        return created
