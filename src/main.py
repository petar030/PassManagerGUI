import sys
from PyQt6.QtWidgets import QApplication
from ui import PasswordManagerApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    initial_file = sys.argv[1] if len(sys.argv) > 1 else None
    window = PasswordManagerApp(initial_file)
    window.show()
    sys.exit(app.exec())
