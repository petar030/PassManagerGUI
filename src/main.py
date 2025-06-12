import sys
from PyQt6.QtWidgets import QApplication
from ui import PasswordManagerApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordManagerApp()
    window.show()
    sys.exit(app.exec())
