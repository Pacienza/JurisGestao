from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QAbstractItemView
)
from .client_form import ClientFormDialog

class ClientsView(QWidget):
    def __init__(self, client_service, auth_service, current_user, permset: set[str]):
        super().__init__()
        self.svc = client_service
        self.auth = auth_service
        self.current_user = current_user
        self.permset = permset
        self._build_ui()
        self._apply_perm_rules()
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

        # + Observações
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Nome", "E-mail", "Telefone", "Documento", "Responsável", "Observações"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # UX: duplo-clique para editar
        self.table.itemDoubleClicked.connect(lambda *_: self._edit())

        layout.addLayout(btns)
        layout.addWidget(self.table)

        self.btn_new.clicked.connect(self._new)
        self.btn_edit.clicked.connect(self._edit)
        self.btn_del.clicked.connect(self._delete)
        self.btn_refresh.clicked.connect(self._refresh)

    def _apply_perm_rules(self):
        self.btn_new.setEnabled("clients.create" in self.permset)
        self.btn_edit.setEnabled(("clients.update_all" in self.permset) or ("clients.update_own" in self.permset))
        self.btn_del.setEnabled(("clients.delete_all" in self.permset) or ("clients.delete_own" in self.permset))

    def _refresh(self):
        rows = self.svc.list_clients(self.current_user, self.permset)
        self.table.setRowCount(0)
        for c in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(c.id)))
            self.table.setItem(row, 1, QTableWidgetItem(c.name or ""))
            self.table.setItem(row, 2, QTableWidgetItem(c.email or ""))
            self.table.setItem(row, 3, QTableWidgetItem(c.phone or ""))
            self.table.setItem(row, 4, QTableWidgetItem(c.document or ""))
            self.table.setItem(row, 5, QTableWidgetItem(c.responsible.username if c.responsible else ""))
            # preview limpo de quebras de linha
            preview = (c.notes or "").replace("\n", " ")[:120]
            self.table.setItem(row, 6, QTableWidgetItem(preview))
        self.table.resizeColumnsToContents()

    def _selected_id(self) -> int | None:
        r = self.table.currentRow()
        if r < 0:
            return None
        it = self.table.item(r, 0)
        return int(it.text()) if it else None

    def _new(self):
        if "clients.create" not in self.permset:
            QMessageBox.warning(self, "Acesso negado", "Sem permissão para criar clientes.")
            return
        allow_assign = ("clients.assign_responsible" in self.permset) or ("clients.update_all" in self.permset)
        responsibles = [(u.id, u.username) for u in self.auth.list_users_by_role("advogado")] if allow_assign else []
        dlg = ClientFormDialog(self, allow_assign=allow_assign, responsibles=responsibles)
        if dlg.exec():
            vals = dlg.values()
            self.svc.create_client(current_user=self.current_user, permset=self.permset, **vals)
            self._refresh()

    def _edit(self):
        cid = self._selected_id()
        if cid is None:
            QMessageBox.information(self, "Editar", "Selecione um cliente.")
            return
        c = self.svc.get_client(cid)
        # robustez: registro pode ter sido removido em outra sessão
        if not c:
            QMessageBox.warning(self, "Cliente", "Registro não encontrado (pode ter sido removido).")
            self._refresh()
            return
        allow_assign = ("clients.assign_responsible" in self.permset) or ("clients.update_all" in self.permset)
        responsibles = [(u.id, u.username) for u in self.auth.list_users_by_role("advogado")] if allow_assign else []
        dlg = ClientFormDialog(self, client=c, allow_assign=allow_assign, responsibles=responsibles)
        if dlg.exec():
            vals = dlg.values()
            try:
                self.svc.update_client(cid, current_user=self.current_user, permset=self.permset, **vals)
                self._refresh()
            except PermissionError as e:
                QMessageBox.warning(self, "Acesso negado", str(e))

    def _delete(self):
        cid = self._selected_id()
        if cid is None:
            QMessageBox.information(self, "Excluir", "Selecione um cliente.")
            return
        if QMessageBox.question(self, "Excluir", "Confirma excluir este cliente?") == QMessageBox.Yes:
            try:
                self.svc.delete_client(cid, current_user=self.current_user, permset=self.permset)
                self._refresh()
            except PermissionError as e:
                QMessageBox.warning(self, "Acesso negado", str(e))
