import sys
from PySide6.QtWidgets import QApplication
from ui.root_window import RootWindow
from core.auth import AuthService
from core.config import DEV_MODE
from core.rbac import RBACService

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("JurisGestão")
    app.setOrganizationName("Seu Escritório") # Personalizar de acordo com escritório do cliente

    auth = AuthService()
    auth.create_schema_if_needed()

    if DEV_MODE:
        #Garante roles, permissões e atribuições padrão no ambiente de desenvolvimento
        auth.get_or_create_roles()
        rbac = RBACService()
        rbac.get_or_create_permissions()
        rbac.assign_default_permissions_to_roles()
        auth.seed_one_actor_per_role()

    win = RootWindow(auth_service=auth)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
