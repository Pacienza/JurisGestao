from __future__ import annotations
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QCheckBox, QFrame
)

class LoginView(QWidget):
    def __init__(self, auth_service, on_login_ok):
        super().__init__()
        self.auth_service = auth_service
        self.on_login_ok = on_login_ok
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(16)

        wrapper = QFrame()
        card = QVBoxLayout(wrapper)
        card.setContentsMargins(32, 32, 32, 32)
        card.setSpacing(12)

        title = QLabel("JurisGestão CRM")
        subtitle = QLabel("Acesse com suas credenciais")
        title.setObjectName("title")
        subtitle.setObjectName("subtitle")

        form = QFormLayout()
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Usuário ou e-mail")
        regex = QRegularExpression(r"^([\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}|[\w\.-]{3,})$")
        self.input_user.setValidator(QRegularExpressionValidator(regex, self))

        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("senha")
        self.input_pass.setEchoMode(QLineEdit.Password)

        self.chk_show = QCheckBox("mostrar senha")
        self.chk_show.toggled.connect(
            lambda c: self.input_pass.setEchoMode(QLineEdit.Normal if c else QLineEdit.Password)
        )

        self.btn_login = QPushButton("Entrar")
        self.btn_login.setDefault(True)
        self.btn_login.clicked.connect(self._handle_login)

        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName("status")

        form.addRow("Usuário", self.input_user)
        form.addRow("Senha", self.input_pass)
        form.addRow("", self.chk_show)

        btns = QHBoxLayout()
        btns.addStretch(1)
        btns.addWidget(self.btn_login)

        card.addWidget(title)
        card.addWidget(subtitle)
        card.addLayout(form)
        card.addLayout(btns)
        card.addWidget(self.lbl_status)

        root.addStretch(1)
        root.addWidget(wrapper, alignment=Qt.AlignHCenter)
        root.addStretch(1)

def _handle_login(self):
        user = self.input_user.text().strip()
        pwd = self.input_pass.text()
        if not user or not pwd:
            self.lbl_status.setText("Preencha usuário e senha.")
            return
        account = self.auth_service.authenticate(user, pwd)
        if account:
            self.lbl_status.setText("")
            self.on_login_ok(account=account)
        else:
            self.lbl_status.setText("Credenciais inválidas.")