"""Application entry point"""

import sys
import os

# Add parent directory to path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPalette, QColor
from pathlib import Path

from ui.main_window import MainWindow


def get_asset_path(relative_path: str) -> Path:
    """PyInstallerでパッケージ化された場合とそうでない場合の両方でアセットパスを取得"""
    if getattr(sys, 'frozen', False):
        # PyInstallerでパッケージ化された場合
        base_path = Path(sys._MEIPASS)
    else:
        # 通常の実行の場合
        base_path = Path(__file__).parent
    return base_path / relative_path


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

    # Fusionスタイルを強制適用（全端末で統一された見た目にする）
    app.setStyle(QStyleFactory.create("Fusion"))

    # macOS Lightテーマに合わせたパレットを設定
    palette = QPalette()
    # 背景色
    palette.setColor(QPalette.Window, QColor("#F5F5F7"))
    palette.setColor(QPalette.WindowText, QColor("#1D1D1F"))
    palette.setColor(QPalette.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.AlternateBase, QColor("#F0F0F2"))
    palette.setColor(QPalette.ToolTipBase, QColor("#FFFFFF"))
    palette.setColor(QPalette.ToolTipText, QColor("#1D1D1F"))
    palette.setColor(QPalette.Text, QColor("#1D1D1F"))
    palette.setColor(QPalette.Button, QColor("#FFFFFF"))
    palette.setColor(QPalette.ButtonText, QColor("#1D1D1F"))
    palette.setColor(QPalette.BrightText, QColor("#FF3B30"))
    palette.setColor(QPalette.Link, QColor("#007AFF"))
    palette.setColor(QPalette.Highlight, QColor("#007AFF"))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    # 無効時の色
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#8E8E93"))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#8E8E93"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#8E8E93"))
    app.setPalette(palette)

    # アプリケーション全体のアイコンを設定（ICOファイルを優先）
    icon_path = get_asset_path("assets/icons/icon.ico")
    if not icon_path.exists():
        icon_path = get_asset_path("assets/icons/icon.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Show main window
    window = MainWindow()
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

