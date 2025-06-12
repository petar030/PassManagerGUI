from PyQt6.QtGui import QIcon, QAction

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLineEdit, QTextEdit, QLabel, QFileDialog,
    QMessageBox, QInputDialog, QDialog, QToolBar, QStyle
)
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox,
    QPushButton, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import Qt, QSize

from api import PasswordManagerAPI
from dialogs import PasswordSetupDialog, EntryDetailsDialog

class PasswordManagerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Offline Password Manager")
        self.resize(600, 400)

        self.api = PasswordManagerAPI() 

        self.current_filepath = None  
        self.is_modified = False

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        #Toolbar
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        toolbar.setContentsMargins(0, 0, 0, 0)

        # Actions
        new_act = QAction(QIcon.fromTheme("document-new"), "New", self)
        load_act = QAction(QIcon.fromTheme("document-open"), "Load", self)
        save_act = QAction(QIcon.fromTheme("document-save"), "Save", self)
        save_as_act = QAction(QIcon.fromTheme("document-save-as"), "Save As", self)
        add_act = QAction(QIcon.fromTheme("list-add"), "Add", self)
        del_act = QAction(QIcon.fromTheme("list-remove"), "Delete", self)
        for act in (new_act, load_act, save_act, save_as_act, add_act, del_act):
            toolbar.addAction(act)

        self.layout.addWidget(toolbar)

        self.list_widget = QListWidget()
        self.list_widget.setSortingEnabled(True)
        
        self.layout.addWidget(self.list_widget)

        new_act.triggered.connect(self.new_file)
        load_act.triggered.connect(self.load_file)
        save_act.triggered.connect(self.save_file)
        save_as_act.triggered.connect(self.save_file_as)
        add_act.triggered.connect(self.add_entry)
        del_act.triggered.connect(self.delete_entry)
        self.list_widget.itemDoubleClicked.connect(self.show_entry_details)



    def new_file(self):
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "The current file is not saved. Are you sure you want to create a new one?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return  

        self.api.reset()
        self.current_filepath = None
        self.is_modified = False
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        for entry in self.api.data["entries"]:
            self.list_widget.addItem(entry["name"])

    def load_file(self):
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "The current file is not saved. Are you sure you want to load other file?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                return 

        path, _ = QFileDialog.getOpenFileName(
            self, "Open .pass file", "", "Pass Files (*.pass);;All Files (*)"
        )
        if not path:
            return

        while True:
            password, ok = QInputDialog.getText(
                self, "Enter Password", "Password:",
                QLineEdit.EchoMode.Password
            )

            if not ok:
                QMessageBox.warning(self, "Canceled", "Loading canceled by user.")
                return

            if self.api.load_from_file(path, password):
                self.current_filepath = path
                self.is_modified = False
                self.refresh_list()
                QMessageBox.information(self, "Success", f"Loaded from {path}")
                return
            else:
                QMessageBox.critical(self, "Invalid Password", "Incorrect password. Try again.")
    
    def save_file(self):
        if self.current_filepath is None:
            self.save_file_as()
            return
        if self.api.save_to_file(self.current_filepath):
            self.is_modified = False
            QMessageBox.information(self, "Success", f"Saved to {self.current_filepath}")
        else:
            QMessageBox.critical(self, "Error", "Failed to save file.")

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save .pass file", "", "Pass Files (*.pass);;All Files (*)"
        )
        if not path:
            return

        if not path.endswith(".pass"):
            path += ".pass"

        dialog = PasswordSetupDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Canceled", "Save canceled by user.")
            return

        password = dialog.password

        if self.api.save_to_file(path, password):
            self.current_filepath = path
            self.is_modified = False
            QMessageBox.information(self, "Success", f"Saved to {path}")
        else:
            QMessageBox.critical(self, "Error", "Failed to save file.")

    def add_entry(self):
        name, ok = QInputDialog.getText(self, "Add Entry", "Name:")
        if not ok or not name.strip():
            return
        username, ok = QInputDialog.getText(self, "Add Entry", "Username:")
        if not ok:
            return
        password, ok = QInputDialog.getText(self, "Add Entry", "Password:")
        if not ok:
            return
        notes, ok = QInputDialog.getMultiLineText(self, "Add Entry", "Notes:")
        if not ok:
            return

        if not self.api.add_entry(name.strip(), username, password, notes):
            QMessageBox.warning(self, "Warning", f"Entry with name '{name}' already exists.")
            return

        self.refresh_list()
        self.is_modified = True

    def delete_entry(self):
        current_item = self.list_widget.currentItem()
        if current_item is None:
            QMessageBox.warning(self, "Warning", "No entry selected to delete.")
            return
        name = current_item.text()
        if QMessageBox.question(self, "Confirm Delete", f"Delete entry '{name}'?") == QMessageBox.StandardButton.Yes:
            if self.api.delete_entry(name):
                self.refresh_list()
                self.is_modified = True
                
            else:
                QMessageBox.warning(self, "Warning", f"Entry '{name}' not found.")

    def show_entry_details(self, item):
        if item is None:
            return
        name = item.text()
        idx = self.api.find_entry_index(name)
        if idx == -1:
            return
        entry = self.api.data["entries"][idx]

        dlg = EntryDetailsDialog(entry, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            updated_entry = dlg.get_entry_data()


            if updated_entry["name"] != name and self.api.find_entry_index(updated_entry["name"]) != -1:
                QMessageBox.warning(self, "Warning", "Entry with this name already exists.")
                return

            if updated_entry["name"] != name:
                self.api.delete_entry(name)
                self.api.add_entry(
                    updated_entry["name"],
                    updated_entry.get("username", ""),
                    updated_entry.get("password", ""),
                    updated_entry.get("notes", "")
                )
            else:
                self.api.edit_entry(
                    name,
                    username=updated_entry.get("username", ""),
                    password=updated_entry.get("password", ""),
                    notes=updated_entry.get("notes", "")
                )

            self.refresh_list()
            self.is_modified = True
            items = self.list_widget.findItems(updated_entry["name"], Qt.MatchFlag.MatchExactly)
            if items:
                self.list_widget.setCurrentItem(items[0])

    def closeEvent(self, event):
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "The current file is not saved. Are you sure you want to exit?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel

            )

            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
                event.accept()
                
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
                


