from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QTimeEdit, QPushButton, QComboBox
)
from PySide6.QtCore import QTime
from datetime import datetime


class AppointmentFormDialog(QDialog):
    def __init__(self, parent=None, current_user=None, permset=None, clients=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Compromisso")
        self.setModal(True)
        self.current_user = current_user
        self.permset = permset
        self.clients = clients or []

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Cliente
        self.cbo_client = QComboBox()
        for client in self.clients:
            self.cbo_client.addItem(client.name, client.id)
        layout.addWidget(QLabel("Cliente"))
        layout.addWidget(self.cbo_client)

        # Tipo de compromisso
        self.cbo_kind = QComboBox()
        self.cbo_kind.addItems(["Reunião", "Audiência", "Visita", "Datas Próximas"])
        layout.addWidget(QLabel("Tipo"))
        layout.addWidget(self.cbo_kind)

        # Horário inicial e final
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime.currentTime())
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime.currentTime().addSecs(3600))
        layout.addWidget(QLabel("Início"))
        layout.addWidget(self.start_time)
        layout.addWidget(QLabel("Término"))
        layout.addWidget(self.end_time)

        # Observações
        self.txt_notes = QTextEdit()
        layout.addWidget(QLabel("Notas"))
        layout.addWidget(self.txt_notes)

        # Botões
        btn_box = QHBoxLayout()
        self.btn_ok = QPushButton("Salvar")
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(self.btn_ok)
        btn_box.addWidget(self.btn_cancel)
        layout.addLayout(btn_box)

    def get_data(self):
        return {
            "client_id": self.cbo_client.currentData(),
            "kind": self.cbo_kind.currentText(),
            "start_time": self.start_time.time().toPython(),
            "end_time": self.end_time.time().toPython(),
            "notes": self.txt_notes.toPlainText(),
        }
