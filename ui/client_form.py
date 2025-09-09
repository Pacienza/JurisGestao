from __future__ import annotations
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QDialogButtonBox, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt

class ClientFormDialog(QDialog):
    def __init__(self, parent=None, *, client=None,
                allow_assign: bool=False, responsibles: list[tuple[int,str]]|None=None):
        super().__init__(parent)
        self.client = client
        self.allow_assign = allow_assign
        self.responsibles = responsibles or []
        self.setWindowTitle("Editar cliente" if client else "Novo cliente")
        self._build_ui()
        if client:
            self._fill(client)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.in_name = QLineEdit()
        self.in_email = QLineEdit()
        self.in_phone = QLineEdit()
        self.in_document = QLineEdit()
        self.in_notes = QTextEdit()
        self.in_notes.setMinimumHeight(80)

        form.addRow("Nome*", self.in_name)
        form.addRow("E-mail", self.in_email)
        form.addRow("Telefone", self.in_phone)
        form.addRow("Documento", self.in_document)
        form.addRow("Observações", self.in_notes)

        # Combo de responsável (somente se permitido)
        self.cb_resp = None
        if self.allow_assign:
            self.cb_resp = QComboBox()
            for uid, uname in self.responsibles:
                self.cb_resp.addItem(uname, uid)
            form.addRow("Responsável", self.cb_resp)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self._accept)
        self.buttons.rejected.connect(self.reject)

        layout.addLayout(form)
        layout.addWidget(self.buttons)

    def _fill(self, c):
        self.in_name.setText(c.name or "")
        self.in_email.setText(c.email or "")
        self.in_phone.setText(c.phone or "")
        self.in_document.setText(c.document or "")
        self.in_notes.setPlainText(c.notes or "")
        if self.cb_resp and c.responsible:
            # seleciona responsável existente
            for i in range(self.cb_resp.count()):
                if self.cb_resp.itemData(i) == c.responsible.id:
                    self.cb_resp.setCurrentIndex(i)
                    break

    def _accept(self):
        if not self.in_name.text().strip():
            QMessageBox.warning(self, "Campos obrigatórios", "Informe o nome do cliente.")
            return
        self.accept()

    def values(self):
        responsible_id = None
        if self.cb_resp:
            responsible_id = int(self.cb_resp.currentData())
        return dict(
            name=self.in_name.text().strip(),
            email=(self.in_email.text().strip() or None),
            phone=(self.in_phone.text().strip() or None),
            document=(self.in_document.text().strip() or None),
            notes=(self.in_notes.toPlainText().strip() or None),
            responsible_id=responsible_id,
        )
