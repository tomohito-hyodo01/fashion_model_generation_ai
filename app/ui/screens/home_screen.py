"""Home screen - Top page with card-based navigation"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from ui.styles import Styles, Colors, Fonts, Spacing, BorderRadius


class ActionCard(QFrame):
    """アクションカードウィジェット"""

    clicked = Signal()

    def __init__(self, title: str, description: str, icon: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.icon = icon
        self._setup_ui()
        self._add_shadow()

    def _setup_ui(self):
        """UIをセットアップ"""
        self.setFixedSize(280, 320)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        layout.setSpacing(Spacing.MD)
        layout.setAlignment(Qt.AlignCenter)

        # アイコン
        icon_label = QLabel(self.icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 64px;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(icon_label)

        layout.addSpacing(Spacing.MD)

        # タイトル
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Fonts.SIZE_XL};
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title_label)

        # 説明
        desc_label = QLabel(self.description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-size: {Fonts.SIZE_SM};
                background: transparent;
                border: none;
                line-height: 1.5;
            }}
        """)
        layout.addWidget(desc_label)

    def _update_style(self):
        """スタイルを更新"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: {BorderRadius.XL}px;
            }}
            QFrame:hover {{
                background-color: {Colors.BG_CARD_HOVER};
                border-color: {Colors.PRIMARY};
            }}
        """)

    def _add_shadow(self):
        """シャドウを追加"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

    def mousePressEvent(self, event):
        """マウスプレスイベント"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def update_styles(self):
        """テーマ変更時にスタイルを更新"""
        self._update_style()


class HomeScreen(QWidget):
    """ホーム画面（トップページ）"""

    navigate_to_generation = Signal()
    navigate_to_edit = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        layout.setSpacing(Spacing.XL)

        # 背景スタイル
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_MAIN};
            }}
        """)

        # 上部スペーサー
        layout.addStretch(1)

        # タイトルエリア
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(Spacing.SM)
        title_container.setStyleSheet("background: transparent;")

        # メインタイトル
        main_title = QLabel("Virtual Model Generator")
        main_title.setAlignment(Qt.AlignCenter)
        main_title.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: 36px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        title_layout.addWidget(main_title)

        # サブタイトル
        subtitle = QLabel("〜 AIバーチャルモデル生成システム 〜")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-size: {Fonts.SIZE_LG};
                font-weight: 400;
                background: transparent;
                border: none;
            }}
        """)
        title_layout.addWidget(subtitle)

        layout.addWidget(title_container)

        layout.addSpacing(Spacing.XXL)

        # カードエリア
        cards_container = QWidget()
        cards_layout = QHBoxLayout(cards_container)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(Spacing.XXL)
        cards_layout.setAlignment(Qt.AlignCenter)
        cards_container.setStyleSheet("background: transparent;")

        # 新規生成カード
        self.card_generation = ActionCard(
            title="新規生成",
            description="衣類画像からAIモデルを生成します。\n参考人物や背景も設定できます。",
            icon="✨"
        )
        self.card_generation.clicked.connect(self.navigate_to_generation.emit)
        cards_layout.addWidget(self.card_generation)

        # チャット修正・履歴カード
        self.card_history = ActionCard(
            title="チャット修正・履歴",
            description="過去の生成結果を確認・修正できます。\nチャットで細かい調整も可能です。",
            icon="📋"
        )
        self.card_history.clicked.connect(self.navigate_to_edit.emit)
        cards_layout.addWidget(self.card_history)

        layout.addWidget(cards_container)

        # 下部スペーサー
        layout.addStretch(2)

    def update_styles(self):
        """テーマ変更時にスタイルを更新"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_MAIN};
            }}
        """)
        self.card_generation.update_styles()
        self.card_history.update_styles()
