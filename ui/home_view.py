from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from datetime import datetime
from PySide6.QtCore import Qt


class HomeView(QWidget):
    def __init__(self, agenda_service, current_user, permset):
        super().__init__()
        self.agenda_service = agenda_service
        self.current_user = current_user
        self.permset = permset

        self._build_ui()
        self._load_appointments()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.lbl_title = QLabel("Bem-vindo ao JurisGestão")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_title)

        self.lbl_summary = QLabel("Resumo do dia:")
        self.lbl_summary.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.lbl_summary)

        self.btn_dev = QPushButton("Dev Tools (ROOT)")
        self.btn_dev.clicked.connect(self._open_dev_tools)
        layout.addWidget(self.btn_dev)

        if self.current_user.username != "root":
            self.btn_dev.hide()

    def _load_appointments(self):
        today = datetime.today().date()
        try:
            appointments = self.agenda_service.list_day(self.current_user, self.permset, today)
            summary = f"Você tem {len(appointments)} compromisso(s) para hoje."
        except Exception as e:
            summary = f"[Erro] Falha ao carregar compromissos: {e}"

        self.lbl_summary.setText(summary)

    def _open_dev_tools(self):
        # Aqui você pode adicionar um diálogo ou outra interface de desenvolvedor
        print("[DEBUG] Dev Tools abertas para root.")
