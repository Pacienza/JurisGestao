from __future__ import annotations
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QLabel, QVBoxLayout, QWidget,
    QStatusBar, QMessageBox
)

from .login_view import LoginView
from .users_view import UsersView
from .clients_view import ClientsView          # <- NOVO: tela de clientes
from core.config import DEV_MODE
from core.rbac import RBACService
from core.clients import ClientService         # <- NOVO: serviço de clientes


class HomeView(QWidget):
    """Tela simples pós-login."""
    def __init__(self, username: str | None = None):
        super().__init__()
        layout = QVBoxLayout(self)
        msg = QLabel(f"Bem-vindo(a), {username or 'usuário'}! 🎉")
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

        # Área central com navegação por pilha (telas)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Serviços e estado
        self.auth = auth_service
        self.rbac = RBACService()              # resolve permissões do usuário
        self.clients = ClientService()         # <- CRIADO: usado por ClientsView
        self.current_user = None
        self.permset: set[str] = set()         # conjunto de permissões efetivas

        # Tela de login (passa o objeto User no callback)
        self.login_view = LoginView(self.auth, on_login_ok=self._go_home)
        self.stack.addWidget(self.login_view)

        # Menus/estilos
        self._build_menu()
        self._apply_qss()
        self._apply_menu_permissions()         # estado inicial (sem permissões)

    # -------- Navegação --------
    def _go_home(self, account):
        """Chamado após login bem-sucedido."""
        self.current_user = account
        self.permset = self.rbac.effective_permissions(account)

        self.home = HomeView(username=account.username)
        self.stack.addWidget(self.home)
        self.stack.setCurrentWidget(self.home)
        self.statusBar().showMessage("Autenticado com sucesso", 3000)

        # Atualiza visibilidade de menus conforme permissões
        self._apply_menu_permissions()

    def _open_users(self):
        """Abre a tela de usuários (requer users.view)."""
        if "users.view" not in self.permset:
            QMessageBox.warning(self, "Acesso negado", "Sem permissão para visualizar usuários.")
            return
        self.users_view = UsersView(self.auth, permset=self.permset)
        self.stack.addWidget(self.users_view)
        self.stack.setCurrentWidget(self.users_view)

    def _open_clients(self):
        """Abre a tela de clientes.
        Visível se houver qualquer permissão de clientes (ver own/all ou criar)."""
        if not ({"clients.view_all", "clients.view_own", "clients.create"} & self.permset):
            QMessageBox.warning(self, "Acesso negado", "Sem permissão para acessar clientes.")
            return
        # Passa também 'auth' para preencher o combo de Responsável quando permitido
        self.clients_view = ClientsView(self.clients, self.auth, self.current_user, self.permset)
        self.stack.addWidget(self.clients_view)
        self.stack.setCurrentWidget(self.clients_view)

    # -------- Menus / Dev --------
    def _build_menu(self):
        # Aplicativo
        self.menu_app = self.menuBar().addMenu("Aplicativo")
        self.act_logout = QAction("Logout", self)
        self.act_logout.triggered.connect(self._logout)
        self.menu_app.addAction(self.act_logout)

        # Cadastros
        self.menu_cad = self.menuBar().addMenu("Cadastros")

        self.act_users = QAction("Usuários", self)
        self.act_users.triggered.connect(self._open_users)
        self.menu_cad.addAction(self.act_users)

        self.act_clients = QAction("Clientes", self)    # <- NOVO
        self.act_clients.triggered.connect(self._open_clients)
        self.menu_cad.addAction(self.act_clients)

        # Menu Dev (opcional)
        if DEV_MODE:
            dev = self.menuBar().addMenu("Dev")
            act_reset = QAction("Recriar banco (DANGER)", self)
            act_seed  = QAction("Seed usuários/roles", self)
            act_list  = QAction("Listar usuários", self)
            act_showp = QAction("Mostrar permissões", self)   # <- NOVO: debug rápido

            act_reset.triggered.connect(self._dev_reset_db)
            act_seed.triggered.connect(self._dev_seed)
            act_list.triggered.connect(self._dev_list_users)
            act_showp.triggered.connect(self._dev_show_perms)

            dev.addAction(act_reset)
            dev.addAction(act_seed)
            dev.addAction(act_list)
            dev.addAction(act_showp)

    def _apply_menu_permissions(self):
        """Mostra/oculta itens do menu conforme permissões atuais."""
        # Usuários
        self.act_users.setVisible("users.view" in self.permset)
        # Clientes: aparece se tiver qualquer permissão de clientes útil
        can_clients = bool({"clients.view_all", "clients.view_own", "clients.create"} & self.permset)
        self.act_clients.setVisible(can_clients)

    def _logout(self):
        """Limpa sessão e volta ao login."""
        self.current_user = None
        self.permset.clear()
        self.stack.setCurrentWidget(self.login_view)
        self._apply_menu_permissions()
        self.statusBar().showMessage("Sessão encerrada", 3000)

    # -------- Ações Dev (opcionais) --------
    def _dev_reset_db(self):
        if QMessageBox.question(
            self, "Recriar banco", "Isto APAGARÁ TODOS OS DADOS. Continuar?"
        ) == QMessageBox.Yes:
            self.auth.reset_database()
            self.statusBar().showMessage("Banco recriado", 3000)

    def _dev_seed(self):
        # Garante permissões + associações + usuários de seed
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

    def _dev_show_perms(self):
        if not self.current_user:
            QMessageBox.information(self, "Permissões", "Nenhum usuário logado.")
            return
        perms = "\n".join(sorted(self.permset)) or "(sem permissões)"
        QMessageBox.information(self, "Permissões efetivas",
                                f"Usuário: {self.current_user.username}\n\n{perms}")

    # -------- Estilo --------
    def _apply_qss(self):
        self.setStyleSheet("""
            QMainWindow { background: #0f1419; }
            QLabel#title { font-size: 22px; font-weight: 700; color: #e6edf3; }
            QLabel#subtitle { color: #9da7b3; font-size: 14px; }
            QLabel#status { color: #ff8080; padding-top: 6px; }
        """)
