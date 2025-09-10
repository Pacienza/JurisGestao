from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication
from ui.login_view import LoginView
from ui.root_window import RootWindow
from core.auth import AuthService

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("JurisGestão")
    app.setOrganizationName("Bento e Gervásio Advocacia")

    auth = AuthService()
    auth.create_schema_if_needed()
    auth.ensure_root_user()  # cria root se necessário

    def on_login_ok(user):
        window = RootWindow(auth_service=auth)
        window.current_user = user
        window._go_home(user)
        window.show()

    login = LoginView(auth_service=auth, on_login_ok=on_login_ok)
    login.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()