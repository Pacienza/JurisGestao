from __future__ import annotations
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QLabel, QVBoxLayout, QWidget, QStatusBar, QMessageBox
from .login_view import LoginView
from .users_view import UsersView
from core.config import DEV_MODE
from core.rbac import RBACService

class HomeView(QWidget):
    def __init__(self, username: str | None = None):
        super().__init__()
        layout = QVBoxLayout(self)
        msg = QLabel(f"Bem-vindo(a), {username or 'usuário'}! ")
        msg.setAlignment(Qt.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(msg)
        layout.addStretch(1)

class RootWindow(QMainWindow):
    def __init__(self, auth_service):
        super().__init__()
        self.setWindowTitle("JurisGestão - Development Mode 0.1.6 [BETA]")
        self.resize(800, 600)
        self.setMinimumSize(400, 300)
        self.setMaximumSize(1200, 900)
        self.setStatusBar(QStatusBar())
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.auth = auth_service
        self.rbac = RBACService()
        self.current_user = None
        self.permset = set()
        
        self.login_view = LoginView(self.auth, on_login_ok=self._go_home)
        self.stack.addWidget(self.login_view)

        self._build_menu()
        self._apply_qss()

def _go_home(self, account):
        self.current_user = account
        self.permset = self.rbac.effective_permissions(account)

        self.home = HomeView(username=account.username)
        self.stack.addWidget(self.home)
        self.stack.setCurrentWidget(self.home)
        self.statusBar().showMessage("Autenticado com sucesso", 3000)

        # Ajusta menu conforme permissões
        self._apply_menu_permissions()

def _open_users(self):
    if "users.view" not in self.permset:
        QMessageBox.warning(self, "Acesso negado", "Você não tem permissão para visualizar usuários.")
    return
    self.users_view = UsersView(self.auth, permset=self.permset)
    self.stack.addWidget(self.users_view)
    self.stack.setCurrentWidget(self.users_view)

    def _build_menu(self):
        self.menu_app = self.menuBar().addMenu("Aplicativo")
        self.act_logout = QAction("Logout", self)
        self.act_logout.triggered.connect(self._logout)
        self.menu_app.addAction(self.act_logout)

        self.menu_cad = self.menuBar().addMenu("Cadastros")
        self.act_users = QAction("Usuários", self)
        self.act_users.triggered.connect(self._open_users)
        self.menu_cad.addAction(self.act_users)

        if DEV_MODE:
            dev = self.menuBar().addMenu("Dev")
            act_reset = QAction("Recriar banco (DANGER)", self)
            act_seed = QAction("Seed usuários/roles", self)
            act_list = QAction("Listar usuários", self)
            act_reset.triggered.connect(self._dev_reset_db)
            act_seed.triggered.connect(self._dev_seed)
            act_list.triggered.connect(self._dev_list_users)
            dev.addAction(act_reset)
            dev.addAction(act_seed)
            dev.addAction(act_list)

        # Inicialmente, sem usuário logado, esconda entradas sensíveis
        self._apply_menu_permissions()

    def _apply_menu_permissions(self):
        # Esconde/mostra 'Usuários' conforme permissão de view
        can_view_users = "users.view" in self.permset
        self.act_users.setVisible(can_view_users)

    def _logout(self):
        self.current_user = None
        self.permset = set()
        self.stack.setCurrentWidget(self.login_view)
        self._apply_menu_permissions()
        self.statusBar().showMessage("Sessão encerrada", 3000)


    # --- Dev actions ---
    def _dev_reset_db(self):
        if QMessageBox.question(self, "Recriar banco",
                                "Isto APAGARÁ TODOS OS DADOS. Continuar?") == QMessageBox.Yes:
            self.auth.reset_database()
            self.statusBar().showMessage("Banco recriado", 3000)

    def _dev_seed(self):
        from core.rbac import RBACService
        r = RBACService(self.auth.session_factory)
        r.get_or_create_permissions()
        r.assign_default_permissions_to_roles()
        created = self.auth.seed_one_actor_per_role()
        if created:
            QMessageBox.information(self, "Seed", f"Usuários criados: {created}")
        else:
            QMessageBox.information(self, "Seed", "Nenhum usuário criado (já existiam).")

    def _dev_list_users(self):
        users = self.auth.list_users()
        if not users:
            QMessageBox.information(self, "Usuários", "Nenhum usuário encontrado.")
            return
        lines = [f"[{uid}] {uname} <{email}> ativo={active}" for uid, uname, email, active in users]
        QMessageBox.information(self, "Usuários", "\n".join(lines))

    def _apply_qss(self):
        self.setStyleSheet("""
            QMainWindow { background: #0f1419; }
            QLabel#title { font-size: 22px; font-weight: 700; color: #e6edf3; }
            QLabel#subtitle { color: #9da7b3; font-size: 14px; }
            QLabel#status { color: #ff8080; padding-top: 6px; }
        """)
