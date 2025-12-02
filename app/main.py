"""Application entry point"""

import sys
import os

# Add parent directory to path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from pathlib import Path

from ui.main_window import MainWindow


def main():
    """Main function"""
    # Windowsでタスクバーにアイコンを表示するための設定
    if sys.platform == 'win32':
        import ctypes
        # AppUserModelIDを設定（Windowsタスクバーでアイコンを正しく表示するため）
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('VirtualFashion.VirtualModelGenerator.1.0')

    # Create application (High DPI support is automatic in Qt 6)
    app = QApplication(sys.argv)
    app.setApplicationName("Virtual Model Generator")
    app.setOrganizationName("VirtualFashion")

    # アプリケーション全体のアイコンを設定
    icon_path = Path(__file__).parent / "assets" / "icons" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Show main window
    window = MainWindow()
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

