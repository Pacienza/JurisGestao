from datetime import datetime, date
from sqlalchemy import select, delete
from core.db import SessionLocal as Session
from core.models import Appointment, Availability


class AgendaService:
    def list_day(self, user, permset, target_date: date):
        with Session() as db:
            stmt = select(Appointment).where(
                Appointment.user_id == user.id,
                Appointment.date == target_date
            ).order_by(Appointment.start_time)
            return db.scalars(stmt).all()

    def list_month(self, user, permset, year: int, month: int):
        with Session() as db:
            stmt = select(Appointment).where(
                Appointment.user_id == user.id,
                Appointment.date >= date(year, month, 1),
                Appointment.date < date(year, month, 28)  # assume no mais de 28
            )
            return db.scalars(stmt).all()

    def is_available(self, user, target_date: date):
        with Session() as db:
            exists = db.scalars(
                select(Availability.id).where(
                    Availability.user_id == user.id,
                    Availability.date == target_date
                )
            ).first()
            return exists is not None

    def toggle_availability(self, user, target_date: date):
        with Session() as db:
            if self.is_available(user, target_date):
                db.execute(
                    delete(Availability).where(
                        Availability.user_id == user.id,
                        Availability.date == target_date
                    )
                )
            else:
                db.add(Availability(user_id=user.id, date=target_date))
            db.commit()

    def create_appointment(self, user, permset, date, start, end, kind, notes, client_id):
        with Session() as db:
            appt = Appointment(
                user_id=user.id,
                client_id=client_id,
                date=date,
                start_time=start,
                end_time=end,
                kind=kind,
                notes=notes,
                created_at=datetime.now()
            )
            db.add(appt)
            db.commit()

    def delete_appointment(self, appt_id: int):
        with Session() as db:
            db.execute(delete(Appointment).where(Appointment.id == appt_id))
            db.commit()

    def list_appointments(self, user):
        with Session() as db:
            stmt = select(Appointment).where(Appointment.user_id == user.id)
            return db.scalars(stmt).all()
