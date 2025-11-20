"""API key configuration dialog"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QFormLayout,
    QMessageBox,
)

from utils.api_key_manager import APIKeyManager


class APIKeyDialog(QDialog):
    """APIキー設定ダイアログ"""

    def __init__(self, api_key_manager: APIKeyManager, parent=None):
        super().__init__(parent)
        self.api_key_manager = api_key_manager
        self.setWindowTitle("APIキー設定")
        self.setMinimumWidth(500)
        self._setup_ui()
        self._load_existing_keys()

    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout(self)

        # OpenAI
        openai_group = self._create_api_key_group(
            "OpenAI API Key",
            "https://platform.openai.com/api-keys",
        )
        self.openai_input = openai_group.findChild(QLineEdit)
        layout.addWidget(openai_group)

        # Stability AI
        stability_group = self._create_api_key_group(
            "Stability AI API Key",
            "https://platform.stability.ai/account/keys",
        )
        self.stability_input = stability_group.findChild(QLineEdit)
        layout.addWidget(stability_group)

        # Google Cloud
        google_group = QGroupBox("Google Imagen 4 API Key")
        google_layout = QFormLayout()
        
        self.google_input = QLineEdit()
        self.google_input.setEchoMode(QLineEdit.Password)
        google_layout.addRow("API Key:", self.google_input)
        
        help_label = QLabel(
            '<a href="https://aistudio.google.com/apikey">Gemini API Keyを取得</a> '
            '（簡易）または '
            '<a href="https://cloud.google.com/iam/docs/service-accounts">Service Account</a> '
            '（本格）'
        )
        help_label.setOpenExternalLinks(True)
        google_layout.addRow("", help_label)
        
        google_group.setLayout(google_layout)
        layout.addWidget(google_group)

        # ボタン
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save_keys)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("キャンセル")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _create_api_key_group(self, title: str, help_url: str) -> QGroupBox:
        """APIキーグループを作成"""
        group = QGroupBox(title)
        layout = QFormLayout()

        # 入力フィールド
        input_field = QLineEdit()
        input_field.setEchoMode(QLineEdit.Password)
        layout.addRow("キー:", input_field)

        # ヘルプリンク
        help_label = QLabel(f'<a href="{help_url}">取得方法</a>')
        help_label.setOpenExternalLinks(True)
        layout.addRow("", help_label)

        group.setLayout(layout)
        return group

    def _load_existing_keys(self):
        """既存のキーを読み込み"""
        openai_key = self.api_key_manager.load_api_key("openai")
        if openai_key:
            self.openai_input.setText(openai_key)

        stability_key = self.api_key_manager.load_api_key("stability")
        if stability_key:
            self.stability_input.setText(stability_key)

        google_key = self.api_key_manager.load_api_key("google")
        if google_key:
            self.google_input.setText(google_key)

    def _save_keys(self):
        """キーを保存"""
        try:
            # OpenAI
            openai_key = self.openai_input.text().strip()
            if openai_key:
                self.api_key_manager.save_api_key("openai", openai_key)

            # Stability AI
            stability_key = self.stability_input.text().strip()
            if stability_key:
                self.api_key_manager.save_api_key("stability", stability_key)

            # Google Cloud
            google_key = self.google_input.text().strip()
            if google_key:
                self.api_key_manager.save_api_key("google", google_key)

            QMessageBox.information(self, "成功", "APIキーを保存しました。")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "エラー", f"保存に失敗しました: {e}")

