"""Edit screen - History, gallery and chat refinement page"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QSplitter,
    QScrollArea,
    QPushButton,
    QProgressBar,
)
from PySide6.QtCore import Qt, Signal
from PIL import Image
from typing import List, Dict, Optional

from ui.styles import Styles, Colors, Fonts, Spacing, BorderRadius
from ui.widgets.gallery_view import GalleryView
from ui.widgets.history_panel import HistoryPanel
from ui.widgets.chat_refinement import ChatRefinementWidget


class EditScreen(QWidget):
    """修正画面（履歴・ギャラリー・チャット修正）"""

    # シグナル
    image_selected = Signal(Image.Image, int)  # 画像選択時
    refinement_requested = Signal(str, dict)  # 修正リクエスト
    video_regeneration_requested = Signal(Image.Image)  # 動画再生成リクエスト
    history_item_selected = Signal(int, list, dict)  # history_id, images, parameters
    video_edit_requested = Signal(Image.Image, str)  # 動画修正リクエスト

    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.current_images: List[Image.Image] = []
        self.current_metadata: Dict = {}
        self._setup_ui()

    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.MD)

        # 背景
        self.setStyleSheet(f"background-color: {Colors.BG_MAIN};")

        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setStyleSheet(Styles.PROGRESS_BAR)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)

        # メインスプリッター（3カラム）
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(Styles.SPLITTER)

        # ===== 左: 履歴パネル =====
        history_group = self._create_history_group()
        splitter.addWidget(history_group)

        # ===== 中央: ギャラリー =====
        gallery_group = self._create_gallery_group()
        splitter.addWidget(gallery_group)

        # ===== 右: チャット修正 =====
        chat_group = self._create_chat_group()
        splitter.addWidget(chat_group)

        # スプリッター幅設定
        splitter.setSizes([280, 500, 320])

        layout.addWidget(splitter)

    def _create_history_group(self) -> QGroupBox:
        """履歴グループを作成"""
        group = QGroupBox("生成履歴")
        group.setStyleSheet(Styles.GROUP_BOX)
        group.setMinimumWidth(250)
        group.setMaximumWidth(350)

        layout = QVBoxLayout()
        layout.setContentsMargins(Spacing.SM, Spacing.LG, Spacing.SM, Spacing.SM)

        # 履歴パネル
        self.history_panel = HistoryPanel(self.history_manager)
        self.history_panel.history_selected.connect(self._on_history_selected)
        layout.addWidget(self.history_panel)

        group.setLayout(layout)
        return group

    def _create_gallery_group(self) -> QGroupBox:
        """ギャラリーグループを作成"""
        group = QGroupBox("生成結果")
        group.setStyleSheet(Styles.GROUP_BOX)

        layout = QVBoxLayout()
        layout.setContentsMargins(Spacing.SM, Spacing.LG, Spacing.SM, Spacing.SM)

        # スクロールエリア
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(Styles.SCROLL_AREA)

        # ギャラリービュー
        self.gallery_view = GalleryView()
        self.gallery_view.image_selected.connect(self._on_gallery_image_selected)

        scroll_area.setWidget(self.gallery_view)
        layout.addWidget(scroll_area)

        group.setLayout(layout)
        return group

    def _create_chat_group(self) -> QGroupBox:
        """チャット修正グループを作成"""
        group = QGroupBox("チャットで修正")
        group.setStyleSheet(Styles.GROUP_BOX)
        group.setMinimumWidth(300)
        group.setMaximumWidth(400)

        layout = QVBoxLayout()
        layout.setContentsMargins(Spacing.MD, Spacing.LG, Spacing.MD, Spacing.MD)

        # チャットウィジェット
        self.chat_widget = ChatRefinementWidget()
        self.chat_widget.refinement_requested.connect(self._on_refinement_requested)
        layout.addWidget(self.chat_widget)

        group.setLayout(layout)
        return group

    # ===== イベントハンドラ =====

    def _on_history_selected(self, history_id: int, images: list, parameters: dict):
        """履歴が選択された時"""
        # ギャラリーに画像を表示
        if images:
            self.current_images = images
            self.gallery_view.set_images(images, parameters)
        # MainWindowにも通知
        self.history_item_selected.emit(history_id, images, parameters)

    def _on_gallery_image_selected(self, image: Image.Image, index: int):
        """ギャラリーで画像が選択された時"""
        self.image_selected.emit(image, index)

    def _on_refinement_requested(self, instruction: str, context: dict):
        """修正リクエストが発生した時"""
        self.refinement_requested.emit(instruction, context)

    def _on_video_regeneration_requested(self, image: Image.Image):
        """動画再生成リクエストが発生した時"""
        self.video_regeneration_requested.emit(image)

    def _on_video_edit_requested(self, source_image: Image.Image, video_path: str):
        """動画修正リクエストが発生した時"""
        self.video_edit_requested.emit(source_image, video_path)

    # ===== 公開メソッド =====

    def set_images(self, images: List[Image.Image], metadata: Dict):
        """画像を設定"""
        self.current_images = images
        self.current_metadata = metadata
        self.gallery_view.set_images(images, metadata)

    def set_video(self, video_path: str, source_image: Optional[Image.Image] = None):
        """動画を設定"""
        self.gallery_view.set_video(video_path, source_image)

    def clear_gallery(self):
        """ギャラリーをクリア"""
        self.current_images = []
        self.current_metadata = {}
        self.gallery_view.clear()

    def set_chat_image(self, image: Image.Image, params: Dict):
        """チャット修正用の画像を設定"""
        self.chat_widget.set_current_image(image, params)

    def set_video_source_image(self, source_image: Image.Image, video_path: str, params: Dict):
        """動画修正用のソース画像を設定"""
        self.chat_widget.set_video_source_image(source_image, video_path, params)

    def on_refinement_completed(self, new_image: Image.Image, ai_response: str):
        """修正完了時の処理"""
        self.chat_widget.on_refinement_completed(new_image, ai_response)

    def on_refinement_failed(self, error_message: str):
        """修正失敗時の処理"""
        self.chat_widget.on_refinement_failed(error_message)

    def set_progress(self, message: str, value: int):
        """進捗を設定"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{message} - %p%")

    def hide_progress(self):
        """進捗を非表示"""
        self.progress_bar.setVisible(False)
        self.progress_bar.setFormat("%p%")

    def refresh_history(self):
        """履歴を更新"""
        self.history_panel.refresh()

    def get_images(self) -> List[Image.Image]:
        """現在の画像を取得"""
        return self.current_images

    def update_styles(self):
        """テーマ変更時にスタイルを更新"""
        self.setStyleSheet(f"background-color: {Colors.BG_MAIN};")
