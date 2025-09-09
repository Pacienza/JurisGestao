from sqlalchemy import select
from core.db import SessionLocal
from core.models import User, Role

def main():
    with SessionLocal() as db:
        u = db.scalars(select(User).where(User.username == "advogada")).first()
        r = db.scalars(select(Role).where(Role.name == "advogado")).first()
        if not u:
            print("Usuária 'advogada' não encontrada.")
            return
        if not r:
            print("Papel 'advogado' não encontrado.")
            return
        u.roles = [r]
        db.commit()
        print("✔ Papel da usuária 'advogada' atualizado para 'advogado'.")

if __name__ == "__main__":
    main()
