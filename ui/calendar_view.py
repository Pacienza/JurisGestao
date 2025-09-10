from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QGridLayout, QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from datetime import date
from ui.appointment_form import AppointmentFormDialog


class AgendaView(QWidget):
    def __init__(self, agenda_service, client_service, auth_service, current_user, permset):
        super().__init__()
        self.agenda = agenda_service
        self.clients = client_service
        self.auth = auth_service
        self.current_user = current_user
        self.permset = permset
        self.selected_date = date.today()

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.lbl_day = QLabel()
        self.lbl_day.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_day)

        self.calendar = QGridLayout()
        layout.addLayout(self.calendar)

        self._build_calendar()

        self.refresh_day()

    def _build_calendar(self):
        today = date.today()
        self.lbl_day.setText(f"<b>{today.strftime('%d/%m/%Y')}</b>")

        for week in range(5):
            for weekday in range(7):
                cell = QFrame()
                cell.setFrameShape(QFrame.Box)
                cell.setFixedSize(80, 60)
                self.calendar.addWidget(cell, week, weekday)

                s_date = today  # Você pode melhorar essa lógica para renderizar o mês corretamente
                cell.mousePressEvent = (lambda d=s_date: lambda event: self._select_day(d))()

    def _select_day(self, d):
        self.selected_date = d
        self.lbl_day.setText(f"<b>{d.strftime('%d/%m/%Y')}</b>")
        self.refresh_day()

    def refresh_day(self):
        self._refresh_day()

    def _refresh_day(self):
        try:
            items = self.agenda.list_day(self.current_user, self.permset, self.selected_date)
            print(f"[DEBUG] Itens do dia: {items}")
        except Exception as e:
            print(f"[ERROR] Falha ao listar compromissos: {e}")

    def _open_popup(self, day):
        dlg = AppointmentFormDialog(
            parent=self,
            current_user=self.current_user,
            permset=self.permset,
            selected_date=day,
            client_service=self.clients,
            agenda_service=self.agenda
        )
        if dlg.exec():
            self.refresh_day()
