from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView
)
from .user_form import UserFormDialog

class UsersView(QWidget):
    def __init__(self, auth_service, permset: set[str] | None = None):
        super().__init__()
        self.auth = auth_service
        self.permset = permset or set()
        self._build_ui()
        self._apply_perm_rules()          # <- NOME CORRETO
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        btns = QHBoxLayout()
        self.btn_new = QPushButton("Novo")
        self.btn_edit = QPushButton("Editar")
        self.btn_del = QPushButton("Excluir")
        self.btn_refresh = QPushButton("Recarregar")
        btns.addWidget(self.btn_new)
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_del)
        btns.addStretch(1)
        btns.addWidget(self.btn_refresh)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Usuário", "E-mail", "Ativo", "Papéis"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout.addLayout(btns)
        layout.addWidget(self.table)

        self.btn_new.clicked.connect(self._new)
        self.btn_edit.clicked.connect(self._edit)
        self.btn_del.clicked.connect(self._delete)
        self.btn_refresh.clicked.connect(self._refresh)

    def _apply_perm_rules(self):
        self.btn_new.setEnabled("users.create" in self.permset)
        self.btn_edit.setEnabled("users.update" in self.permset)
        self.btn_del.setEnabled("users.delete" in self.permset)

    def _refresh(self):
        users = self.auth.list_users()
        self.table.setRowCount(0)
        for (uid, uname, email, active) in users:
            u = self.auth.get_user(uid)  # para exibir papéis
            roles = ", ".join(sorted([r.name for r in u.roles])) if u else ""
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(uid)))
            self.table.setItem(row, 1, QTableWidgetItem(uname))
            self.table.setItem(row, 2, QTableWidgetItem(email))
            self.table.setItem(row, 3, QTableWidgetItem("Sim" if active else "Não"))
            self.table.setItem(row, 4, QTableWidgetItem(roles))
        self.table.resizeColumnsToContents()

    def _current_user_id(self) -> int | None:
        sel = self.table.currentRow()
        if sel < 0:
            return None
        item = self.table.item(sel, 0)
        return int(item.text()) if item else None

    def _new(self):
        if "users.create" not in self.permset:
            QMessageBox.warning(self, "Acesso negado", "Sem permissão para criar usuários.")
            return
        dlg = UserFormDialog(self.auth, self)
        if dlg.exec():
            self._refresh()

    def _edit(self):
        if "users.update" not in self.permset:
            QMessageBox.warning(self, "Acesso negado", "Sem permissão para editar usuários.")
            return
        uid = self._current_user_id()
        if uid is None:
            QMessageBox.information(self, "Editar", "Selecione um usuário.")
            return
        user = self.auth.get_user(uid)
        dlg = UserFormDialog(self.auth, self, user=user)
        if dlg.exec():
            self._refresh()

    def _delete(self):
        if "users.delete" not in self.permset:
            QMessageBox.warning(self, "Acesso negado", "Sem permissão para excluir usuários.")
            return
        uid = self._current_user_id()
        if uid is None:
            QMessageBox.information(self, "Excluir", "Selecione um usuário.")
            return
        if QMessageBox.question(self, "Excluir", "Confirma excluir este usuário?") == QMessageBox.Yes:
            self.auth.delete_user(uid)
            self._refresh()
