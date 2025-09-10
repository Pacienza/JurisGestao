from PySide6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox, QMenuBar, QMenu
from PySide6.QtGui import QAction
from ui.login_view import LoginView
from ui.home_view import HomeView
from ui.users_view import UsersView
from ui.clients_view import ClientsView
from ui.calendar_view import AgendaView
from core.auth import AuthService
from core.agenda import AgendaService
from core.clients import ClientService
from core.rbac import RBACService


class RootWindow(QMainWindow):
    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.setWindowTitle("JurisGestão")
        self.setGeometry(100, 100, 1000, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.auth = auth_service
        self.rbac = RBACService(self.auth.session_factory)
        self.agenda = AgendaService()
        self.clients = ClientService()

        self.current_user = None
        self.permset = set()

        self._build_menu()

        self.login_view = LoginView(self.auth, self._go_home)
        self.stack.addWidget(self.login_view)
        self.stack.setCurrentWidget(self.login_view)

    def _build_menu(self):
        self.menu = QMenuBar()
        self.setMenuBar(self.menu)

        self.act_users = QAction("Usuários", self)
        self.act_users.triggered.connect(self._open_users)
        self.menu_file.addAction(self.act_users)

        self.act_clients = QAction("Clientes", self)
        self.act_clients.triggered.connect(self._open_clients)
        self.menu_file.addAction(self.act_clients)

        self.menu_file = QMenu("Menu", self)
        self.menu.addMenu(self.menu_file)

        self.act_home = QAction("Início", self)
        self.act_home.triggered.connect(self._open_home)
        self.menu_file.addAction(self.act_home)

        self.act_agenda = QAction("Agenda", self)
        self.act_agenda.triggered.connect(self._open_agenda)
        self.menu_file.addAction(self.act_agenda)

        self.act_logout = QAction("Logout", self)
        self.act_logout.triggered.connect(self._logout)
        self.menu_file.addAction(self.act_logout)

        self.menu_dev = QMenu("Dev", self)
        self.menu.addMenu(self.menu_dev)

        self.act_debug = QAction("Debug", self)
        self.act_debug.triggered.connect(self._debug)
        self.menu_dev.addAction(self.act_debug)

        self.menu_dev.menuAction().setVisible(False)  # Oculto por padrão

    def _open_users(self):
        self.users_view = UsersView(auth_service=self.auth, permset=self.permset)
        self.stack.addWidget(self.users_view)
        self.stack.setCurrentWidget(self.users_view)


    def _open_clients(self):
        self.clients_view = ClientsView(
            client_service=self.clients,
            auth_service=self.auth,
            current_user=self.current_user,
            permset=self.permset
        )
        self.stack.addWidget(self.clients_view)
        self.stack.setCurrentWidget(self.clients_view)



    def _apply_menu_permissions(self):
        is_root = getattr(self.current_user, "username", "") == "root"
        self.menu_dev.menuAction().setVisible(is_root)

        if hasattr(self, "act_users"):
            self.act_users.setVisible("users.view" in self.permset)

        if hasattr(self, "act_clients"):
            self.act_clients.setVisible(bool({
                "clients.create", "clients.view_all", "clients.view_own"
            } & self.permset))

    def _go_home(self, user):
        self.current_user = user
        self.permset = self.rbac.effective_permissions(user)

        self.home_view = HomeView(
            current_user=self.current_user,
            agenda_service=self.agenda,
            permset=self.permset
        )
        self.agenda_view = AgendaView(
            agenda_service=self.agenda,
            client_service=self.clients,
            auth_service=self.auth,
            current_user=self.current_user,
            permset=self.permset,
        )

        self.stack.addWidget(self.home_view)
        self.stack.addWidget(self.agenda_view)

        self._apply_menu_permissions()
        self.stack.setCurrentWidget(self.home_view)
        self.statusBar().showMessage("Autenticado com sucesso", 3000)

    def _open_home(self):
        if hasattr(self, "home_view"):
            self.home_view.refresh()
            self.stack.setCurrentWidget(self.home_view)

    def _open_agenda(self):
        if hasattr(self, "agenda_view"):
            self.agenda_view.refresh()
            self.stack.setCurrentWidget(self.agenda_view)

    def _logout(self):
        confirm = QMessageBox.question(
            self,
            "Logout",
            "Tem certeza que deseja sair?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.current_user = None
            self.permset.clear()
            self._apply_menu_permissions()
            self.stack.setCurrentWidget(self.login_view)
            self.statusBar().showMessage("Logout efetuado", 3000)

    def _debug(self):
        QMessageBox.information(self, "Debug", "Modo desenvolvedor ativado.")
