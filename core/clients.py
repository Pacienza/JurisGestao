from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .db import SessionLocal
from .models import Client, User

class ClientService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def get_client(self, client_id: int) -> Optional[Client]:
        with self.session_factory() as db:
            return db.scalars(
                select(Client)
                .options(selectinload(Client.responsible))
                .where(Client.id == client_id)
            ).first()

    def list_clients(self, current_user: User, permset: set[str]) -> list[Client]:
        with self.session_factory() as db:
            stmt = select(Client).options(selectinload(Client.responsible))
            if "clients.view_all" in permset:
                pass
            elif "clients.view_own" in permset:
                stmt = stmt.where(Client.responsible_id == current_user.id)
            else:
                return []
            return db.scalars(stmt.order_by(Client.id.desc())).all()

    def create_client(
        self, *, name: str, email: str | None, phone: str | None,
        document: str | None, notes: str | None, responsible_id: int | None,
        current_user: User, permset: set[str]
    ) -> Client:
        if "clients.create" not in permset:
            raise PermissionError("Sem permissão para criar clientes.")
        # quem pode escolher outro responsável?
        can_assign = ("clients.assign_responsible" in permset) or ("clients.update_all" in permset)
        resp_id = responsible_id if (responsible_id and can_assign) else current_user.id

        with self.session_factory() as db:
            c = Client(
                name=name, email=email or None, phone=phone or None,
                document=document or None, notes=notes or None,
                created_by_id=current_user.id, responsible_id=resp_id,
            )
            db.add(c)
            db.commit()
            db.refresh(c)
            return c

    def update_client(
        self, client_id: int, *, name: Optional[str]=None, email: Optional[str]=None,
        phone: Optional[str]=None, document: Optional[str]=None, notes: Optional[str]=None,
        responsible_id: Optional[int]=None, current_user: User=None, permset: set[str]=frozenset()
    ) -> Client:
        with self.session_factory() as db:
            c = db.get(Client, client_id)
            if not c:
                raise ValueError("Cliente não encontrado.")

            owns = (c.responsible_id == current_user.id)
            can_all = "clients.update_all" in permset
            can_own = "clients.update_own" in permset and owns
            if not (can_all or can_own):
                raise PermissionError("Sem permissão para editar este cliente.")

            if name is not None: c.name = name
            if email is not None: c.email = email or None
            if phone is not None: c.phone = phone or None
            if document is not None: c.document = document or None
            if notes is not None: c.notes = notes or None

            # alterar responsável só para quem pode
            if responsible_id is not None and (("clients.assign_responsible" in permset) or can_all):
                c.responsible_id = responsible_id

            db.commit()
            db.refresh(c)
            return c

    def delete_client(self, client_id: int, *, current_user: User, permset: set[str]) -> None:
        with self.session_factory() as db:
            c = db.get(Client, client_id)
            if not c:
                return
            owns = (c.responsible_id == current_user.id)
            can_all = "clients.delete_all" in permset
            can_own = "clients.delete_own" in permset and owns
            if not (can_all or can_own):
                raise PermissionError("Sem permissão para excluir este cliente.")
            db.delete(c)
            db.commit()
