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
    QProgressBar,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PIL import Image
from typing import List, Dict, Optional
from io import BytesIO

from ui.styles import Styles, Colors, Fonts, BorderRadius


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
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # 送信者ラベル
        sender_label = QLabel("あなた" if self.sender == "user" else "AI")
        sender_label.setStyleSheet(f"""
            font-weight: bold;
            font-size: {Fonts.SIZE_SM};
            color: {Colors.PRIMARY if self.sender == "user" else Colors.ACCENT_GREEN};
            background: transparent;
        """)
        layout.addWidget(sender_label)

        # メッセージテキスト
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        message_label.setStyleSheet(f"""
            padding: 6px 8px;
            background-color: {Colors.BG_CARD};
            border-radius: {BorderRadius.SM}px;
            font-size: {Fonts.SIZE_SM};
            color: {Colors.TEXT_PRIMARY};
        """)
        layout.addWidget(message_label)

        # 画像がある場合は表示
        if self.image:
            image_label = QLabel()
            pixmap = self._pil_to_pixmap(self.image)
            # 画像サイズを親ウィジェットの幅に合わせて調整（最大220px）
            max_size = 220
            scaled_pixmap = pixmap.scaled(max_size, max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignLeft)
            image_label.setStyleSheet("background: transparent;")
            layout.addWidget(image_label)

        # スタイル設定
        bg_color = Colors.PRIMARY_LIGHT if self.sender == "user" else Colors.SUCCESS_LIGHT
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: {BorderRadius.MD}px;
                margin: 3px 0px;
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
    video_refinement_requested = Signal(str, dict)  # instruction, context (動画修正用)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.conversation_history: List[Dict] = []
        self.current_image: Optional[Image.Image] = None
        self.original_params: Optional[Dict] = None
        # 動画修正モード用
        self.is_video_mode: bool = False
        self.video_source_image: Optional[Image.Image] = None
        self.video_path: Optional[str] = None
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
        scroll_area.setStyleSheet(Styles.SCROLL_AREA)

        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background: transparent;")
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

        # プログレスバー（送信ボタンの下に配置、初期は非表示）
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMinimumHeight(28)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("処理中... %p%")
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {Colors.BG_TERTIARY};
                border: none;
                border-radius: {BorderRadius.SM}px;
                text-align: center;
                font-weight: 600;
                font-size: {Fonts.SIZE_SM};
                color: {Colors.TEXT_PRIMARY};
            }}
            QProgressBar::chunk {{
                background-color: {Colors.PRIMARY};
                border-radius: {BorderRadius.SM}px;
            }}
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 初期状態では無効化
        self.setEnabled(False)
    
    def set_current_image(self, image: Image.Image, params: Dict):
        """現在の画像とパラメータを設定"""
        self.current_image = image
        self.original_params = params
        self.conversation_history = []
        # 動画モードをリセット
        self.is_video_mode = False
        self.video_source_image = None
        self.video_path = None

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

    def set_video_source_image(self, source_image: Image.Image, video_path: str, params: Dict):
        """動画修正用のソース画像を設定"""
        self.current_image = source_image
        self.video_source_image = source_image
        self.video_path = video_path
        self.original_params = params
        self.conversation_history = []
        # 動画モードを有効化
        self.is_video_mode = True

        print(f"[Chat Widget] 動画修正モード: ソース画像を設定")
        print(f"[Chat Widget] 動画パス: {video_path}")

        # チャットを有効化
        self.setEnabled(True)
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)

        # チャット履歴をクリア
        self._clear_chat()

        # AI初期メッセージを追加（動画モード用）
        self._add_ai_message(
            "動画の元画像が選択されました！\n"
            "修正したい箇所を教えてください。\n"
            "元画像を修正した後、動画を再生成します。\n"
            "例：「もっと明るく」「背景を変更」「笑顔にして」",
            image=source_image
        )

        print(f"[Chat Widget] 動画修正チャット準備完了")
    
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

        # プログレスバーを表示
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        # 修正リクエストを発火
        context = {
            "image": self.current_image,
            "params": self.original_params,
            "history": self.conversation_history
        }

        # 動画モードの場合は動画修正シグナルを発火
        if self.is_video_mode:
            context["video_path"] = self.video_path
            context["video_source_image"] = self.video_source_image
            self.video_refinement_requested.emit(instruction, context)
        else:
            self.refinement_requested.emit(instruction, context)
    
    def on_refinement_completed(self, new_image: Image.Image, ai_response: str):
        """修正完了時の処理"""
        self.current_image = new_image

        # プログレスバーを非表示
        self.progress_bar.setVisible(False)

        # AIメッセージを追加
        self._add_ai_message(ai_response, image=new_image)

        # 入力を再有効化
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

    def on_video_refinement_completed(self, new_image: Image.Image, video_path: str, ai_response: str):
        """動画修正完了時の処理"""
        self.current_image = new_image
        self.video_source_image = new_image
        self.video_path = video_path

        # プログレスバーを非表示
        self.progress_bar.setVisible(False)

        # AIメッセージを追加（動画再生成完了のメッセージ）
        self._add_ai_message(ai_response, image=new_image)

        # 入力を再有効化
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
    
    def on_refinement_failed(self, error_message: str):
        """修正失敗時の処理"""
        # プログレスバーを非表示
        self.progress_bar.setVisible(False)

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

    def set_progress(self, message: str, value: int):
        """プログレスバーの値を設定"""
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{message} %p%")
        self.progress_bar.setVisible(True)

    def hide_progress(self):
        """プログレスバーを非表示"""
        self.progress_bar.setVisible(False)


