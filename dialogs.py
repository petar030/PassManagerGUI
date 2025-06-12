import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
    QCheckBox, QMessageBox, QHBoxLayout, QApplication
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

class PasswordSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Password")
        self.setModal(True)
        self.resize(300, 150)

        self.layout = QVBoxLayout(self)

        self.layout.addWidget(QLabel(
            "Enter a password (min 8 chars, 1 uppercase, 1 lowercase, 1 digit):"
        ))

        self.pw1 = QLineEdit()
        self.pw1.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw1.setPlaceholderText("Password")
        self.layout.addWidget(self.pw1)

        self.pw2 = QLineEdit()
        self.pw2.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw2.setPlaceholderText("Repeat Password")
        self.layout.addWidget(self.pw2)

        self.show_cb = QCheckBox("Show password")
        self.show_cb.toggled.connect(self.toggle_echo)
        self.layout.addWidget(self.show_cb)

        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Cancel")
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        self.layout.addLayout(btn_layout)

        self.btn_ok.clicked.connect(self.validate)
        self.btn_cancel.clicked.connect(self.reject)

    def toggle_echo(self, show):
        mode = QLineEdit.EchoMode.Normal if show else QLineEdit.EchoMode.Password
        self.pw1.setEchoMode(mode)
        self.pw2.setEchoMode(mode)

    def validate(self):
        p1 = self.pw1.text()
        p2 = self.pw2.text()

        if p1 != p2:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        if len(p1) < 8:
            QMessageBox.warning(self, "Error", "Password must be at least 8 characters.")
            return
        if not re.search(r"[A-Z]", p1):
            QMessageBox.warning(self, "Error", "Must include an uppercase letter.")
            return
        if not re.search(r"[a-z]", p1):
            QMessageBox.warning(self, "Error", "Must include a lowercase letter.")
            return
        if not re.search(r"\d", p1):
            QMessageBox.warning(self, "Error", "Must include a digit.")
            return

        self.password = p1
        self.accept()

class EntryDetailsDialog(QDialog):
    def __init__(self, entry, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Entry Details")
        self.resize(400, 350)

        self.entry_original = entry
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Helper to create an input field with a copy button
        def make_edit_with_copy(widget):
            layout = QHBoxLayout()
            layout.addWidget(widget)

            copy_btn = QPushButton()
            copy_btn.setIcon(QIcon.fromTheme("edit-copy"))
            copy_btn.setFixedSize(24, 24)
            copy_btn.setToolTip("Copy to clipboard")
            layout.addWidget(copy_btn)

            def copy_text():
                clipboard = QApplication.clipboard()
                if isinstance(widget, QLineEdit):
                    clipboard.setText(widget.text())
                elif isinstance(widget, QTextEdit):
                    clipboard.setText(widget.toPlainText())

            copy_btn.clicked.connect(copy_text)
            return layout

        # Create fields
        self.name_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.notes_edit = QTextEdit()

        # Name
        self.layout.addWidget(QLabel("Name:"))
        self.layout.addLayout(make_edit_with_copy(self.name_edit))

        # Username
        self.layout.addWidget(QLabel("Username:"))
        self.layout.addLayout(make_edit_with_copy(self.username_edit))

        # Password
        self.layout.addWidget(QLabel("Password:"))
        self.layout.addLayout(make_edit_with_copy(self.password_edit))

        # Show/hide password
        self.show_password_btn = QPushButton("Show password")
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.toggled.connect(self.toggle_password_visibility)
        self.layout.addWidget(self.show_password_btn)

        # Notes
        self.layout.addWidget(QLabel("Notes:"))
        self.layout.addLayout(make_edit_with_copy(self.notes_edit))

        # Buttons: Edit / Save / Cancel
        buttons_layout = QHBoxLayout()
        self.btn_edit = QPushButton("Edit")
        self.btn_save = QPushButton("Save Changes")
        self.btn_cancel = QPushButton("Cancel")
        buttons_layout.addWidget(self.btn_edit)
        buttons_layout.addWidget(self.btn_save)
        buttons_layout.addWidget(self.btn_cancel)
        self.layout.addLayout(buttons_layout)

        self.btn_edit.clicked.connect(self.enable_editing)
        self.btn_save.clicked.connect(self.save_changes)
        self.btn_cancel.clicked.connect(self.cancel_changes)

        self.set_editable(False)
        self.load_entry(entry)

    def toggle_password_visibility(self, checked):
        self.password_edit.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )
        self.show_password_btn.setText("Hide password" if checked else "Show password")

    def load_entry(self, entry):
        self.name_edit.setText(entry.get("name", ""))
        self.username_edit.setText(entry.get("username", ""))
        self.password_edit.setText(entry.get("password", ""))
        self.notes_edit.setPlainText(entry.get("notes", ""))
        self._original_data = self.get_entry_data()

    def set_editable(self, editable):
        for widget in [self.name_edit, self.username_edit, self.password_edit, self.notes_edit]:
            widget.setReadOnly(not editable)
        self.btn_save.setVisible(editable)
        self.btn_cancel.setVisible(editable)
        self.btn_edit.setVisible(not editable)

    def enable_editing(self):
        self.set_editable(True)

    def save_changes(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Warning", "Name cannot be empty.")
            return
        self.accept()

    def cancel_changes(self):
        self.load_entry(self._original_data)
        self.set_editable(False)

    def get_entry_data(self):
        return {
            "name": self.name_edit.text().strip(),
            "username": self.username_edit.text(),
            "password": self.password_edit.text(),
            "notes": self.notes_edit.toPlainText()
        }

