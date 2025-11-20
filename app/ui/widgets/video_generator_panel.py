"""Video generation panel widget"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QTextEdit,
    QGroupBox,
    QMessageBox,
    QFileDialog,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PIL import Image
from typing import Optional
from pathlib import Path


class VideoGeneratorPanel(QWidget):
    """動画生成パネルウィジェット"""
    
    video_generation_requested = Signal(Image.Image, dict)  # image, settings
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image: Optional[Image.Image] = None
        self.generated_video_path: Optional[str] = None
        self._setup_ui()
    
    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        
        # タイトル
        title_label = QLabel("🎬 動画生成（FASHN AI）")
        title_label.setStyleSheet("font-weight: bold; font-size: 14pt; padding: 10px;")
        layout.addWidget(title_label)
        
        # 説明
        info_label = QLabel(
            "生成された画像から動画を作成します。\n"
            "モデルが回転したり、ポーズを変えたりする動画が生成されます。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 5px; font-size: 9pt;")
        layout.addWidget(info_label)
        
        # 設定グループ
        settings_group = QGroupBox("動画設定")
        settings_layout = QVBoxLayout()
        
        # 動画の長さ
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("動画の長さ:"))
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["5秒", "10秒"])
        self.duration_combo.setCurrentIndex(1)  # デフォルト: 10秒
        duration_layout.addWidget(self.duration_combo)
        duration_layout.addStretch()
        settings_layout.addLayout(duration_layout)
        
        # 解像度
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("解像度:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["480p", "720p", "1080p"])
        self.resolution_combo.setCurrentIndex(2)  # デフォルト: 1080p
        resolution_layout.addWidget(self.resolution_combo)
        resolution_layout.addStretch()
        settings_layout.addLayout(resolution_layout)
        
        # プロンプト
        prompt_label = QLabel("動きの指示（オプション）:")
        prompt_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        settings_layout.addWidget(prompt_label)
        
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText(
            "例: fashion model rotating 360 degrees\n"
            "例: walking on runway\n"
            "例: striking different poses\n"
            "\n空欄の場合は自動で適切な動きが生成されます"
        )
        self.prompt_text.setMaximumHeight(100)
        self.prompt_text.setText(
            "fashion model rotating 360 degrees and striking elegant poses from different angles, "
            "turning left and right, showing front, side and back views, "
            "professional runway modeling, smooth transitions between poses"
        )
        settings_layout.addWidget(self.prompt_text)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # 生成ボタン
        self.generate_btn = QPushButton("🎬 動画を生成")
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.setEnabled(False)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                font-size: 12pt;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        layout.addWidget(self.generate_btn)
        
        # 動画プレビューエリア
        preview_group = QGroupBox("動画プレビュー")
        preview_layout = QVBoxLayout()
        
        # プレースホルダー
        self.preview_label = QLabel("動画を生成すると、ここにプレビューが表示されます")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px dashed #ccc;
                border-radius: 5px;
                color: #999;
            }
        """)
        preview_layout.addWidget(self.preview_label)
        
        # 保存ボタン
        self.save_video_btn = QPushButton("動画を保存")
        self.save_video_btn.setEnabled(False)
        self.save_video_btn.clicked.connect(self._save_video)
        preview_layout.addWidget(self.save_video_btn)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        layout.addStretch()
    
    def set_current_image(self, image: Image.Image):
        """動画生成用の画像を設定"""
        self.current_image = image
        self.generate_btn.setEnabled(True)
        
        print("[Video Generator] 画像が設定されました")
    
    def _on_generate_clicked(self):
        """生成ボタンがクリックされた時"""
        if not self.current_image:
            QMessageBox.warning(self, "警告", "動画生成用の画像が設定されていません")
            return
        
        # 設定を取得
        duration_text = self.duration_combo.currentText()
        duration = int(duration_text.replace("秒", ""))
        
        resolution = self.resolution_combo.currentText()
        
        prompt = self.prompt_text.toPlainText().strip()
        if not prompt:
            prompt = None
        
        settings = {
            "duration": duration,
            "resolution": resolution,
            "prompt": prompt
        }
        
        # シグナルを発火
        self.video_generation_requested.emit(self.current_image, settings)
        
        # ボタンを無効化
        self.generate_btn.setEnabled(False)
    
    def on_video_generated(self, video_path: str):
        """動画生成完了時"""
        self.generated_video_path = video_path
        
        # プレビューラベルを更新
        self.preview_label.setText(f"動画が生成されました\n\n{Path(video_path).name}")
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #e8f5e9;
                border: 2px solid #4caf50;
                border-radius: 5px;
                color: #2e7d32;
                font-weight: bold;
            }
        """)
        
        # ボタンを有効化
        self.generate_btn.setEnabled(True)
        self.save_video_btn.setEnabled(True)
        
        print(f"[Video Generator] 動画生成完了: {video_path}")
    
    def on_video_generation_failed(self, error_message: str):
        """動画生成失敗時"""
        self.preview_label.setText(f"動画生成に失敗しました\n\n{error_message}")
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #ffebee;
                border: 2px solid #f44336;
                border-radius: 5px;
                color: #c62828;
            }
        """)
        
        # ボタンを有効化
        self.generate_btn.setEnabled(True)
        
        print(f"[Video Generator] 動画生成失敗: {error_message}")
    
    def _save_video(self):
        """動画を保存"""
        if not self.generated_video_path:
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "動画を保存",
            "",
            "MP4 動画 (*.mp4)"
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy(self.generated_video_path, save_path)
                QMessageBox.information(self, "成功", f"動画を保存しました:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"保存に失敗しました:\n{e}")


