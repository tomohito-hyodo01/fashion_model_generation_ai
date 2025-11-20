"""Application entry point"""

import sys
import os

# Add parent directory to path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from ui.main_window import MainWindow


def main():
    """Main function"""
    # Create application (High DPI support is automatic in Qt 6)
    app = QApplication(sys.argv)
    app.setApplicationName("Virtual Fashion Try-On")
    app.setOrganizationName("VirtualFashion")

    # Show main window
    window = MainWindow()
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

