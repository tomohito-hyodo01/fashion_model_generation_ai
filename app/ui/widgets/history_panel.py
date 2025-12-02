"""History panel widget"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QGridLayout,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QIcon
from PIL import Image
from io import BytesIO
from typing import List, Dict, Optional
from datetime import datetime

from ui.styles import Styles, Colors


class HistoryItemWidget(QWidget):
    """履歴アイテムウィジェット"""
    
    item_clicked = Signal(int)  # history_id
    favorite_toggled = Signal(int)  # history_id
    delete_requested = Signal(int)  # history_id
    
    def __init__(self, history_data: Dict, thumbnail: Image.Image, parent=None):
        super().__init__(parent)
        self.history_data = history_data
        self.thumbnail = thumbnail
        self._setup_ui()
    
    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # サムネイル
        thumb_label = QLabel()
        pixmap = self._pil_to_pixmap(self.thumbnail)
        scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        thumb_label.setPixmap(scaled_pixmap)
        thumb_label.setFixedSize(80, 80)
        layout.addWidget(thumb_label)
        
        # 情報
        info_layout = QVBoxLayout()
        
        # 日時
        created_at = datetime.fromisoformat(self.history_data["created_at"])
        date_label = QLabel(created_at.strftime("%Y-%m-%d %H:%M"))
        date_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(date_label)
        
        # モード・枚数
        mode_text = "角度違い" if self.history_data["generation_mode"] == "angle" else "種類違い"
        mode_label = QLabel(f"{mode_text} / {self.history_data['num_images']}枚")
        mode_label.setStyleSheet("font-size: 9pt; color: #666;")
        info_layout.addWidget(mode_label)
        
        # タグ
        if self.history_data.get("tags"):
            tags_text = " ".join([f"#{tag}" for tag in self.history_data["tags"]])
            tags_label = QLabel(tags_text)
            tags_label.setStyleSheet("font-size: 8pt; color: #3498db;")
            info_layout.addWidget(tags_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        # ボタン
        btn_layout = QVBoxLayout()
        
        # 削除ボタンのみ（お気に入り機能は削除）
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(30, 30)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.history_data["id"]))
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        # クリック可能に
        self.setCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event):
        """クリック時"""
        if event.button() == Qt.LeftButton:
            self.item_clicked.emit(self.history_data["id"])
    
    def _pil_to_pixmap(self, pil_image: Image.Image) -> QPixmap:
        """PIL画像をQPixmapに変換"""
        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")
        buffer.seek(0)
        
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        return pixmap
    


class HistoryPanel(QWidget):
    """履歴パネルウィジェット"""
    
    history_selected = Signal(int, list, dict)  # history_id, images, parameters
    
    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self._setup_ui()
        self._load_history()
    
    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        
        # フィルターコンボボックス（非表示で保持、内部でのみ使用）
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["すべて", "お気に入り", "種類違い", "角度違い"])
        self.filter_combo.setVisible(False)  # 非表示にする
        
        # 履歴リスト
        self.history_list = QListWidget()
        self.history_list.setSpacing(5)
        self.history_list.setStyleSheet(Styles.LIST_WIDGET + Styles.SCROLL_AREA)
        layout.addWidget(self.history_list)
        
        # 統計情報
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("font-size: 9pt; color: #666; padding: 5px;")
        layout.addWidget(self.stats_label)
    
    def _load_history(self):
        """履歴を読み込み"""
        # 現在のフィルターを取得
        filter_text = self.filter_combo.currentText()
        
        favorites_only = (filter_text == "お気に入り")
        
        # 履歴を取得
        history_list = self.history_manager.get_history_list(
            limit=50,
            favorites_only=favorites_only
        )
        
        # フィルター適用
        if filter_text == "種類違い":
            history_list = [h for h in history_list if h["generation_mode"] == "variety"]
        elif filter_text == "角度違い":
            history_list = [h for h in history_list if h["generation_mode"] == "angle"]
        
        # リストをクリア
        self.history_list.clear()
        
        # アイテムを追加
        for history in history_list:
            # サムネイルを取得
            thumbnails = self.history_manager.get_history_images(
                history["id"],
                thumbnail_only=True
            )
            
            if thumbnails:
                # ウィジェットを作成
                item_widget = HistoryItemWidget(history, thumbnails[0])
                item_widget.item_clicked.connect(self._on_history_clicked)
                item_widget.delete_requested.connect(self._on_delete_requested)
                
                # リストアイテムを作成
                item = QListWidgetItem(self.history_list)
                item.setSizeHint(item_widget.sizeHint())
                self.history_list.addItem(item)
                self.history_list.setItemWidget(item, item_widget)
    
    def _on_filter_changed(self, filter_text: str):
        """フィルターが変更された時"""
        self._load_history()
    
    def _on_history_clicked(self, history_id: int):
        """履歴がクリックされた時"""
        # 画像とパラメータを取得
        images = self.history_manager.get_history_images(history_id)
        
        # 履歴情報を取得
        history_list = self.history_manager.get_history_list(limit=1000)
        history_data = next((h for h in history_list if h["id"] == history_id), None)
        
        if history_data:
            # シグナルを発火
            self.history_selected.emit(history_id, images, history_data["parameters"])
            print(f"[History] 履歴選択: ID={history_id}")
    
    def _on_delete_requested(self, history_id: int):
        """削除が要求された時"""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "確認",
            "この履歴を削除しますか？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.history_manager.delete_history(history_id)
            self._load_history()
            print(f"[History] 履歴削除: ID={history_id}")
    
    def refresh(self):
        """履歴を更新"""
        self._load_history()


