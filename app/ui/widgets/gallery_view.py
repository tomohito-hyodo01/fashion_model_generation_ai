"""Gallery view widget"""

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QScrollArea, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PIL import Image
from io import BytesIO
from typing import List


class GalleryView(QWidget):
    """結果ギャラリービュー"""
    
    image_selected = Signal(Image.Image, int)  # 画像、インデックス

    def __init__(self, parent=None):
        super().__init__(parent)
        self.images: List[Image.Image] = []
        self.metadata = {}
        self.selected_index = -1
        self._setup_ui()

    def _setup_ui(self):
        """UIをセットアップ"""
        from PySide6.QtWidgets import QVBoxLayout

        main_layout = QVBoxLayout(self)

        # スクロールエリア
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # グリッドレイアウトのコンテナ
        container = QWidget()
        self.grid_layout = QGridLayout(container)
        scroll_area.setWidget(container)

        main_layout.addWidget(scroll_area)

    def set_images(self, images: List[Image.Image], metadata: dict):
        """
        画像を設定

        Args:
            images: PIL画像のリスト
            metadata: メタデータ
        """
        self.images = images
        self.metadata = metadata
        self._update_display()

    def get_images(self) -> List[Image.Image]:
        """画像を取得"""
        return self.images

    def clear(self):
        """表示をクリア"""
        self.images = []
        self.metadata = {}
        self._update_display()

    def _update_display(self):
        """表示を更新"""
        # 既存のウィジェットを削除
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # 画像を表示（2列）
        for i, img in enumerate(self.images):
            row = i // 2
            col = i % 2

            # コンテナウィジェットを作成
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(5, 5, 5, 5)

            # PIL画像をQPixmapに変換
            pixmap = self._pil_to_pixmap(img)
            scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # ラベルに設定
            label = QLabel()
            label.setPixmap(scaled_pixmap)
            label.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(label)

            # 選択ボタン
            select_btn = QPushButton("この画像を修正")
            select_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            select_btn.clicked.connect(lambda checked, idx=i, image=img: self._on_image_clicked(image, idx))
            container_layout.addWidget(select_btn)

            self.grid_layout.addWidget(container, row, col)
    
    def _on_image_clicked(self, image: Image.Image, index: int):
        """画像がクリックされた時"""
        self.selected_index = index
        self.image_selected.emit(image, index)

    def _pil_to_pixmap(self, pil_image: Image.Image) -> QPixmap:
        """PIL画像をQPixmapに変換"""
        # PIL画像をバイト列に変換
        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")
        buffer.seek(0)

        # QPixmapに変換
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())

        return pixmap


