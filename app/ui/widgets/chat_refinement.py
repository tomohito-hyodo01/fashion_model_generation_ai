"""Chat-based image refinement widget"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PIL import Image
from typing import List, Dict, Optional
from io import BytesIO


class ChatMessage(QFrame):
    """チャットメッセージウィジェット"""
    
    def __init__(self, sender: str, message: str, image: Optional[Image.Image] = None, parent=None):
        super().__init__(parent)
        self.sender = sender  # "user" or "ai"
        self.message = message
        self.image = image
        self._setup_ui()
    
    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 送信者ラベル
        sender_label = QLabel("あなた" if self.sender == "user" else "AI")
        sender_label.setStyleSheet(f"""
            font-weight: bold;
            color: {"#3498db" if self.sender == "user" else "#2ecc71"};
        """)
        layout.addWidget(sender_label)
        
        # メッセージテキスト
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            padding: 8px;
            background-color: #f8f9fa;
            border-radius: 5px;
        """)
        layout.addWidget(message_label)
        
        # 画像がある場合は表示
        if self.image:
            image_label = QLabel()
            pixmap = self._pil_to_pixmap(self.image)
            scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            layout.addWidget(image_label)
        
        # スタイル設定
        bg_color = "#e3f2fd" if self.sender == "user" else "#f1f8e9"
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 8px;
                margin: 5px;
            }}
        """)
    
    def _pil_to_pixmap(self, pil_image: Image.Image) -> QPixmap:
        """PIL画像をQPixmapに変換"""
        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")
        buffer.seek(0)
        
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        return pixmap


class ChatRefinementWidget(QWidget):
    """チャットベースの画像修正ウィジェット"""
    
    refinement_requested = Signal(str, dict)  # instruction, context
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conversation_history: List[Dict] = []
        self.current_image: Optional[Image.Image] = None
        self.original_params: Optional[Dict] = None
        self._setup_ui()
    
    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        
        # 使い方の説明（タイトルは削除）
        help_text = QLabel(
            "生成された画像に対して、自然な言葉で修正指示を出してください。\n"
            "例: 「もっと明るくして」「背景を青空に変更」「笑顔にして」"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #666; padding: 5px 10px; font-size: 9pt;")
        layout.addWidget(help_text)
        
        # チャット履歴表示エリア
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch()
        
        scroll_area.setWidget(self.chat_container)
        layout.addWidget(scroll_area, stretch=1)
        
        # 入力エリア
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("修正内容を入力してください（例: もっと明るくして）")
        self.input_field.setMinimumHeight(40)
        self.input_field.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.input_field)
        
        # 統一デザインの送信ボタンスタイル
        BUTTON_STYLE = """
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """
        
        self.send_btn = QPushButton("送信")
        self.send_btn.setMinimumSize(80, 40)
        self.send_btn.setStyleSheet(BUTTON_STYLE)
        self.send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        # 初期状態では無効化
        self.setEnabled(False)
    
    def set_current_image(self, image: Image.Image, params: Dict):
        """現在の画像とパラメータを設定"""
        self.current_image = image
        self.original_params = params
        self.conversation_history = []
        
        print(f"[Chat Widget] 画像とパラメータを設定")
        print(f"[Chat Widget] チャットを有効化します")
        
        # チャットを有効化
        self.setEnabled(True)
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        
        # チャット履歴をクリア
        self._clear_chat()
        
        # AI初期メッセージを追加
        self._add_ai_message(
            "画像が選択されました！\n"
            "修正したい箇所があれば、自然な言葉で教えてください。\n"
            "例：「もっと明るく」「背景を変更」「笑顔にして」",
            image=image
        )
        
        print(f"[Chat Widget] チャット準備完了")
    
    def _send_message(self):
        """メッセージを送信"""
        instruction = self.input_field.text().strip()
        
        if not instruction:
            return
        
        # ユーザーメッセージを追加
        self._add_user_message(instruction)
        
        # 入力欄をクリア
        self.input_field.clear()
        
        # 一時的に無効化
        self.send_btn.setEnabled(False)
        self.input_field.setEnabled(False)
        
        # 修正リクエストを発火
        context = {
            "image": self.current_image,
            "params": self.original_params,
            "history": self.conversation_history
        }
        self.refinement_requested.emit(instruction, context)
    
    def on_refinement_completed(self, new_image: Image.Image, ai_response: str):
        """修正完了時の処理"""
        self.current_image = new_image
        
        # AIメッセージを追加
        self._add_ai_message(ai_response, image=new_image)
        
        # 入力を再有効化
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
    
    def on_refinement_failed(self, error_message: str):
        """修正失敗時の処理"""
        self._add_ai_message(f"エラーが発生しました: {error_message}")
        
        # 入力を再有効化
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
    
    def _add_user_message(self, message: str):
        """ユーザーメッセージを追加"""
        msg_widget = ChatMessage("user", message)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg_widget)
        
        # 会話履歴に追加
        self.conversation_history.append({
            "sender": "user",
            "message": message
        })
    
    def _add_ai_message(self, message: str, image: Optional[Image.Image] = None):
        """AIメッセージを追加"""
        msg_widget = ChatMessage("ai", message, image)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg_widget)
        
        # 会話履歴に追加
        self.conversation_history.append({
            "sender": "ai",
            "message": message,
            "has_image": image is not None
        })
    
    def _clear_chat(self):
        """チャット履歴をクリア"""
        # 既存のメッセージウィジェットを削除
        for i in reversed(range(self.chat_layout.count() - 1)):  # stretchは残す
            item = self.chat_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
    
    def get_conversation_history(self) -> List[Dict]:
        """会話履歴を取得"""
        return self.conversation_history.copy()


