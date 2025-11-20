"""Garment slot widget"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
from pathlib import Path

from models.clothing_item import ClothingItem


class GarmentSlotWidget(QWidget):
    """衣類スロットウィジェット"""

    remove_requested = Signal()

    def __init__(self, garment: ClothingItem, parent=None):
        super().__init__(parent)
        self.garment = garment
        self._setup_ui()

    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QHBoxLayout(self)

        # サムネイル
        thumbnail_label = QLabel()
        pixmap = QPixmap(self.garment.image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            thumbnail_label.setPixmap(scaled_pixmap)
        else:
            thumbnail_label.setText("No Image")
        thumbnail_label.setFixedSize(80, 80)
        layout.addWidget(thumbnail_label)

        # 情報
        info_label = QLabel(self.garment.display_name)
        layout.addWidget(info_label)

        layout.addStretch()

        # 削除ボタン
        remove_btn = QPushButton("削除")
        remove_btn.clicked.connect(self.remove_requested.emit)
        layout.addWidget(remove_btn)

