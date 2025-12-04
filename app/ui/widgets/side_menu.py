"""Side navigation menu widget"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.styles import Styles, Colors, Fonts, Spacing, BorderRadius


class SideMenuButton(QPushButton):
    """サイドメニューのボタン"""

    def __init__(self, text: str, icon_text: str = "", parent=None):
        super().__init__(parent)
        self.setText(f"  {icon_text}  {text}" if icon_text else f"  {text}")
        self.setCheckable(True)
        self.setMinimumHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    def _update_style(self):
        """スタイルを更新"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_SECONDARY};
                font-size: {Fonts.SIZE_SM};
                font-weight: 500;
                text-align: left;
                padding: 12px 16px;
                border: none;
                border-radius: {BorderRadius.MD}px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_CARD_HOVER};
                color: {Colors.TEXT_PRIMARY};
            }}
            QPushButton:checked {{
                background-color: {Colors.PRIMARY};
                color: {Colors.TEXT_ON_PRIMARY};
                font-weight: 600;
            }}
            QPushButton:checked:hover {{
                background-color: {Colors.PRIMARY_HOVER};
            }}
        """)


class SideMenu(QWidget):
    """サイドナビゲーションメニュー"""

    screen_changed = Signal(str)  # "home", "generation", "edit"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.buttons = {}
        self._setup_ui()

    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.SM, Spacing.MD, Spacing.SM, Spacing.MD)
        layout.setSpacing(Spacing.XS)

        # 背景スタイル
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_SECONDARY};
                border-right: 1px solid {Colors.BORDER_LIGHT};
            }}
        """)

        # ロゴ/タイトル（クリックでホームに戻る）
        self.title_btn = QPushButton("Virtual Model")
        self.title_btn.setCursor(Qt.PointingHandCursor)
        self.title_btn.setStyleSheet(f"""
            QPushButton {{
                color: {Colors.PRIMARY};
                font-size: {Fonts.SIZE_XL};
                font-weight: 700;
                padding: 16px 8px;
                background: transparent;
                border: none;
            }}
            QPushButton:hover {{
                color: {Colors.PRIMARY_HOVER};
            }}
        """)
        self.title_btn.clicked.connect(self._on_title_clicked)
        layout.addWidget(self.title_btn)

        # 区切り線
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {Colors.BORDER_LIGHT}; border: none; max-height: 1px;")
        layout.addWidget(separator)

        layout.addSpacing(Spacing.MD)

        # メニューボタン
        self.btn_generation = SideMenuButton("新規生成", "✨")
        self.btn_generation.clicked.connect(lambda: self._on_button_clicked("generation"))
        layout.addWidget(self.btn_generation)
        self.buttons["generation"] = self.btn_generation

        self.btn_edit = SideMenuButton("チャット修正・履歴", "📝")
        self.btn_edit.clicked.connect(lambda: self._on_button_clicked("edit"))
        layout.addWidget(self.btn_edit)
        self.buttons["edit"] = self.btn_edit

        # スペーサー
        layout.addStretch()

        # 区切り線（下部）
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet(f"background-color: {Colors.BORDER_LIGHT}; border: none; max-height: 1px;")
        layout.addWidget(separator2)

        layout.addSpacing(Spacing.SM)

        # APIキー設定ボタン（下部に配置）
        self.btn_api_key = SideMenuButton("APIキー設定", "🔑")
        self.btn_api_key.clicked.connect(lambda: self._on_button_clicked("api_key_setup"))
        layout.addWidget(self.btn_api_key)
        self.buttons["api_key_setup"] = self.btn_api_key

        layout.addSpacing(Spacing.SM)

    def _on_button_clicked(self, screen_name: str):
        """ボタンがクリックされた時"""
        # 全てのボタンのチェックを外す
        for name, btn in self.buttons.items():
            btn.setChecked(name == screen_name)

        # シグナルを発火
        self.screen_changed.emit(screen_name)

    def _on_title_clicked(self):
        """タイトルがクリックされた時（ホームに戻る）"""
        # 全てのボタンのチェックを外す
        for btn in self.buttons.values():
            btn.setChecked(False)

        # ホーム画面へ
        self.screen_changed.emit("home")

    def set_current_screen(self, screen_name: str):
        """現在の画面を設定（外部から呼び出し用）"""
        for name, btn in self.buttons.items():
            btn.setChecked(name == screen_name)

    def select_screen(self, screen_name: str):
        """現在の画面を設定（エイリアス）"""
        self.set_current_screen(screen_name)

    def update_styles(self):
        """テーマ変更時にスタイルを更新"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_SECONDARY};
                border-right: 1px solid {Colors.BORDER_LIGHT};
            }}
        """)
        for btn in self.buttons.values():
            btn._update_style()
