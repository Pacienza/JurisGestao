from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QSpacerItem, QSizePolicy, QStyle
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class LoginView(QWidget):
    def __init__(self, auth_service, on_login_ok):
        super().__init__()
        self.auth_service = auth_service
        self.on_login_ok = on_login_ok
        self.resize(500, 360)
        self.setMinimumSize(400, 300)
        self.setWindowTitle("Login - JurisGestão")

        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #CCC;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #005B96;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #007ACC;
            }
        """)


        font = QFont("Segoe UI", 10)
        self.setFont(font)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        layout.addSpacerItem(QSpacerItem(0, 80, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Título
        title = QLabel("JurisGestão")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(20)

        # Campo de usuário
        user_layout = QHBoxLayout()
        user_icon = QLabel()
        user_icon.setPixmap(self.style().standardIcon(QStyle.SP_FileIcon).pixmap(20, 20))
        user_layout.addWidget(user_icon)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuário ou e-mail")
        user_layout.addWidget(self.username_input)
        layout.addLayout(user_layout)

        # Campo de senha
        pass_layout = QHBoxLayout()
        pass_icon = QLabel()
        pass_icon.setPixmap(self.style().standardIcon(QStyle.SP_MessageBoxWarning).pixmap(20, 20))
        pass_layout.addWidget(pass_icon)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Senha")
        pass_layout.addWidget(self.password_input)

        self.password_input.returnPressed.connect(self._handle_login)
        layout.addLayout(pass_layout)

        # Botão de login
        self.login_btn = QPushButton(" Entrar")
        self.login_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOkButton))
        self.login_btn.clicked.connect(self._handle_login)
        layout.addWidget(self.login_btn)

        layout.addSpacerItem(QSpacerItem(0, 80, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _handle_login(self):
        user = self.username_input.text()
        pwd = self.password_input.text()
        account = self.auth_service.authenticate(user, pwd)
        if account:
            self.on_login_ok(account)
        else:
            self.username_input.clear()
            self.password_input.clear()
            self.username_input.setFocus()
