"""API Key Setup Screen - Initial setup for required API keys"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.styles import Styles, Colors, Fonts, Spacing, BorderRadius


class APIKeySetupScreen(QWidget):
    """APIキー設定画面（初回起動時・設定変更時に表示）"""

    setup_completed = Signal()  # 設定完了時に発火

    def __init__(self, api_key_manager, parent=None):
        super().__init__(parent)
        self.api_key_manager = api_key_manager
        self.is_initial_setup = True  # 初回設定かどうか
        self._setup_ui()

    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(Spacing.LG)
        layout.setAlignment(Qt.AlignCenter)

        # コンテナ（中央寄せ、最大幅制限）
        container = QFrame()
        container.setMaximumWidth(600)
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: {BorderRadius.LG}px;
                padding: {Spacing.XL}px;
            }}
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(Spacing.LG)

        # タイトル
        self.title_label = QLabel("APIキーの設定")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: {Spacing.SM}px;
        """)
        container_layout.addWidget(self.title_label)

        # 説明
        self.description_label = QLabel(
            "このアプリケーションを使用するには、以下のAPIキーが必要です。\n"
            "各サービスのウェブサイトでAPIキーを取得してください。"
        )
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet(f"""
            font-size: {Fonts.SIZE_MD};
            color: {Colors.TEXT_SECONDARY};
            padding-bottom: {Spacing.MD}px;
        """)
        container_layout.addWidget(self.description_label)

        # Gemini API キー入力
        gemini_section = self._create_api_key_section(
            "Gemini API キー",
            "Google AI Studioで無料で取得できます",
            "https://aistudio.google.com/app/apikey",
            "gemini"
        )
        container_layout.addLayout(gemini_section)

        container_layout.addSpacing(Spacing.MD)

        # FASHN API キー入力
        fashn_section = self._create_api_key_section(
            "FASHN API キー",
            "FASHN AIのウェブサイトで取得できます",
            "https://fashn.ai/",
            "fashn"
        )
        container_layout.addLayout(fashn_section)

        container_layout.addSpacing(Spacing.LG)

        # 設定完了ボタン
        self.complete_btn = QPushButton("設定を完了して開始")
        self.complete_btn.setMinimumHeight(52)
        self.complete_btn.setCursor(Qt.PointingHandCursor)
        self.complete_btn.setStyleSheet(Styles.BUTTON_SUCCESS)
        self.complete_btn.clicked.connect(self._on_complete_clicked)
        container_layout.addWidget(self.complete_btn)

        # エラーメッセージ
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet(f"""
            font-size: {Fonts.SIZE_SM};
            color: {Colors.ERROR};
        """)
        self.error_label.setVisible(False)
        container_layout.addWidget(self.error_label)

        layout.addWidget(container, alignment=Qt.AlignCenter)

        # 背景色
        self.setStyleSheet(f"background-color: {Colors.BG_MAIN};")

    def _create_api_key_section(self, title: str, description: str, url: str, key_name: str) -> QVBoxLayout:
        """APIキー入力セクションを作成"""
        section = QVBoxLayout()
        section.setSpacing(Spacing.SM)

        # ラベル
        label = QLabel(title)
        label.setStyleSheet(f"""
            font-size: {Fonts.SIZE_MD};
            font-weight: 600;
            color: {Colors.TEXT_PRIMARY};
        """)
        section.addWidget(label)

        # 説明とリンク
        link_label = QLabel(f'{description}: <a href="{url}" style="color: {Colors.PRIMARY};">{url}</a>')
        link_label.setOpenExternalLinks(True)
        link_label.setStyleSheet(f"""
            font-size: {Fonts.SIZE_SM};
            color: {Colors.TEXT_MUTED};
        """)
        section.addWidget(link_label)

        # 入力フィールド
        input_field = QLineEdit()
        input_field.setPlaceholderText(f"{title}を入力...")
        input_field.setEchoMode(QLineEdit.Password)
        input_field.setMinimumHeight(44)
        input_field.setStyleSheet(Styles.INPUT_FIELD)
        section.addWidget(input_field)

        # 入力フィールドを保存
        setattr(self, f"{key_name}_input", input_field)

        return section

    def _on_complete_clicked(self):
        """設定完了ボタンがクリックされた時"""
        gemini_key = self.gemini_input.text().strip()
        fashn_key = self.fashn_input.text().strip()

        # 初回設定時は両方必須
        if self.is_initial_setup:
            if not gemini_key:
                self._show_error("Gemini APIキーを入力してください")
                return
            if not fashn_key:
                self._show_error("FASHN APIキーを入力してください")
                return
        else:
            # 更新時は入力があるものだけ更新
            if not gemini_key and not fashn_key:
                self._show_error("少なくとも1つのAPIキーを入力してください")
                return

        # APIキーを保存
        try:
            if gemini_key:
                self.api_key_manager.save_api_key("gemini", gemini_key)
            if fashn_key:
                self.api_key_manager.save_api_key("fashn", fashn_key)

            # 設定完了シグナルを発火
            self.setup_completed.emit()

        except Exception as e:
            self._show_error(f"APIキーの保存に失敗しました: {e}")

    def _show_error(self, message: str):
        """エラーメッセージを表示"""
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def _hide_error(self):
        """エラーメッセージを非表示"""
        self.error_label.setVisible(False)

    def set_mode(self, is_initial: bool):
        """表示モードを設定（初回設定 / 設定変更）"""
        self.is_initial_setup = is_initial
        self._hide_error()

        # 入力フィールドをクリア
        self.gemini_input.clear()
        self.fashn_input.clear()

        if is_initial:
            self.title_label.setText("APIキーの設定")
            self.description_label.setText(
                "このアプリケーションを使用するには、以下のAPIキーが必要です。\n"
                "各サービスのウェブサイトでAPIキーを取得してください。"
            )
            self.complete_btn.setText("設定を完了して開始")
            self.gemini_input.setPlaceholderText("Gemini API キーを入力...")
            self.fashn_input.setPlaceholderText("FASHN API キーを入力...")
        else:
            self.title_label.setText("APIキーの変更")
            self.description_label.setText(
                "APIキーを変更できます。\n"
                "変更したいキーのみ入力してください（空欄のキーは変更されません）。"
            )
            self.complete_btn.setText("設定を保存")
            # 既存キーがあることを示すプレースホルダー
            gemini_exists = self.api_key_manager.get_api_key("gemini") is not None
            fashn_exists = self.api_key_manager.get_api_key("fashn") is not None
            self.gemini_input.setPlaceholderText(
                "新しいキーを入力（設定済み）" if gemini_exists else "Gemini API キーを入力..."
            )
            self.fashn_input.setPlaceholderText(
                "新しいキーを入力（設定済み）" if fashn_exists else "FASHN API キーを入力..."
            )
