from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QCheckBox,
    QListWidget, QListWidgetItem, QDialogButtonBox, QMessageBox
)

class UserFormDialog(QDialog):
    def __init__(self, auth_service, parent=None, *, user=None):
        super().__init__(parent)
        self.auth = auth_service
        self.user = user  # None => criação
        self.setWindowTitle("Editar usuário" if user else "Novo usuário")
        self._build_ui()
        self._load_roles()
        if user:
            self._fill_from_user(user)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.in_username = QLineEdit()
        self.in_email = QLineEdit()
        self.in_password = QLineEdit()
        self.in_password.setEchoMode(QLineEdit.Password)
        self.chk_active = QCheckBox("Ativo")
        self.lst_roles = QListWidget()
        self.lst_roles.setSelectionMode(QListWidget.MultiSelection)

        form.addRow("Usuário", self.in_username)
        form.addRow("E-mail", self.in_email)
        form.addRow("Senha", self.in_password)
        form.addRow("", self.chk_active)
        form.addRow("Papéis", self.lst_roles)

        layout.addLayout(form)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self._on_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _load_roles(self):
        self.lst_roles.clear()
        for r in self.auth.list_roles():
            item = QListWidgetItem(r.name)
            item.setData(Qt.UserRole, r.name)
            self.lst_roles.addItem(item)

    def _fill_from_user(self, user):
        self.in_username.setText(user.username)
        self.in_email.setText(user.email)
        self.chk_active.setChecked(bool(user.is_active))
        user_role_names = {r.name for r in user.roles}
        for i in range(self.lst_roles.count()):
            item = self.lst_roles.item(i)
            if item.data(Qt.UserRole) in user_role_names:
                item.setSelected(True)

    def _on_accept(self):
        username = self.in_username.text().strip()
        email = self.in_email.text().strip()
        password = self.in_password.text()
        roles = [self.lst_roles.item(i).data(Qt.UserRole)
                for i in range(self.lst_roles.count())
                if self.lst_roles.item(i).isSelected()]
        is_active = self.chk_active.isChecked()

        if not username or not email or (self.user is None and not password):
            QMessageBox.warning(self, "Campos obrigatórios",
                                "Preencha usuário, e-mail e senha (para novo usuário).")
            return

        try:
            if self.user is None:
                self.auth.create_user(username=username, email=email, password=password, roles=roles)
            else:
                self.auth.update_user(self.user.id, username=username, email=email,
                                    password=password or None, is_active=is_active, roles=roles)
        except ValueError as e:
            QMessageBox.critical(self, "Erro ao salvar", str(e))
            return

        self.accept()
