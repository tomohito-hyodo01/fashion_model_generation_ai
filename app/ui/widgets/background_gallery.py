"""Background gallery widget for visual background selection"""

from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QPushButton,
    QToolButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QFileDialog,
    QButtonGroup,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon, QColor, QPainter
from pathlib import Path
from typing import Dict, Optional

from ui.styles import Styles


class BackgroundGalleryWidget(QWidget):
    """背景ギャラリーウィジェット
    
    プリセット背景またはカスタム背景画像を選択できる
    """
    
    background_selected = Signal(str, str, str)  # bg_id, description, image_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_bg_id = "white"  # デフォルト選択
        self.custom_bg_image = None  # カスタム背景画像のパス
        
        # プリセット背景の定義
        self.background_presets = self._load_background_presets()
        
        # ボタングループ（排他的選択のため）
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        self._setup_ui()
    
    def _load_background_presets(self) -> Dict[str, Dict[str, str]]:
        """プリセット背景情報を読み込み"""
        base_path = Path(__file__).parent.parent.parent / "assets" / "backgrounds"
        
        return {
            "white": {
                "name": "白",
                "image": str(base_path / "white.png"),
                "description": "plain solid white background, studio setting",
                "color": "#FFFFFF",
                "emoji": ""
            },
            "gray": {
                "name": "グレー",
                "image": str(base_path / "gray.png"),
                "description": "neutral gray background, professional look",
                "color": "#808080",
                "emoji": ""
            },
            "studio": {
                "name": "スタジオ",
                "image": str(base_path / "studio.png"),
                "description": "professional photo studio background with soft lighting",
                "color": "#E0E0E0",
                "emoji": ""
            },
            "city": {
                "name": "街",
                "image": str(base_path / "city.png"),
                "description": "modern city street background, urban setting",
                "color": "#4A90E2",
                "emoji": ""
            },
            "nature": {
                "name": "自然",
                "image": str(base_path / "nature.png"),
                "description": "natural outdoor setting with trees and greenery",
                "color": "#7CB342",
                "emoji": ""
            },
            "beach": {
                "name": "ビーチ",
                "image": str(base_path / "beach.png"),
                "description": "beach background with sand and ocean",
                "color": "#FFD54F",
                "emoji": ""
            },
            "indoor": {
                "name": "室内",
                "image": str(base_path / "indoor.png"),
                "description": "indoor interior background, modern room",
                "color": "#BCAAA4",
                "emoji": ""
            },
            "abstract": {
                "name": "抽象",
                "image": str(base_path / "abstract.png"),
                "description": "abstract artistic background with soft colors",
                "color": "#CE93D8",
                "emoji": ""
            }
        }
    
    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # タイトル
        title_label = QLabel("背景を選択")
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title_label)
        
        # ギャラリーグリッド
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)  # 隙間を狭める
        
        # プリセット背景ボタンを配置（4列）
        for i, (bg_id, bg_info) in enumerate(self.background_presets.items()):
            row = i // 4
            col = i % 4
            
            # 背景ボタンを作成
            btn = self._create_background_button(bg_id, bg_info)
            grid_layout.addWidget(btn, row, col)
            
            # ボタングループに追加
            self.button_group.addButton(btn)
            
            # デフォルト選択
            if bg_id == self.selected_bg_id:
                btn.setChecked(True)
        
        layout.addLayout(grid_layout)

        layout.addSpacing(10)

        # カスタム背景アップロードボタン（中央配置）
        custom_btn = QPushButton("カスタム背景画像をアップロード")
        custom_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        custom_btn.setMinimumHeight(40)
        custom_btn.setCursor(Qt.PointingHandCursor)
        custom_btn.clicked.connect(self._upload_custom_background)
        layout.addWidget(custom_btn)

        # カスタム背景プレビューエリア（中央配置）
        preview_layout = QHBoxLayout()
        preview_layout.addStretch()

        # カスタム背景プレビュー（選択時に表示）
        self.custom_preview_label = QLabel()
        self.custom_preview_label.setFixedSize(60, 60)
        self.custom_preview_label.setStyleSheet("""
            QLabel {
                border: 3px solid #2ecc71;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
        """)
        self.custom_preview_label.setVisible(False)
        self.custom_preview_label.setScaledContents(True)
        preview_layout.addWidget(self.custom_preview_label)

        # カスタム背景ファイル名
        self.custom_filename_label = QLabel("")
        self.custom_filename_label.setStyleSheet("font-size: 9pt; color: #2ecc71; font-weight: bold;")
        self.custom_filename_label.setVisible(False)
        preview_layout.addWidget(self.custom_filename_label)

        preview_layout.addStretch()
        layout.addLayout(preview_layout)

        layout.addStretch()
    
    def _create_background_button(self, bg_id: str, bg_info: Dict[str, str]) -> QToolButton:
        """背景ボタンを作成（画像の下にテキスト表示）"""
        btn = QToolButton()
        btn.setCheckable(True)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # アイコンの下にテキスト
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.setMinimumSize(110, 130)
        btn.setMaximumSize(140, 160)
        
        # ボタンの内容を設定
        image_path = bg_info["image"]
        name = bg_info["name"]
        
        # 画像が存在するか確認
        if Path(image_path).exists():
            pixmap = QPixmap(image_path)
            btn.setIcon(QIcon(pixmap))
            btn.setIconSize(QSize(90, 90))
        
        # テキスト設定
        btn.setText(name)
        
        # グレーの場合のみグレー背景、それ以外は白背景
        if bg_id == "gray":
            bg_color = "#c0c0c0"
            hover_bg = "#d0d0d0"
            checked_bg = "#b0b0b0"
        else:
            bg_color = "white"
            hover_bg = "#f0f8ff"
            checked_bg = "#e8f8f5"
        
        # スタイル設定
        btn.setStyleSheet(f"""
            QToolButton {{
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: {bg_color};
                font-size: 9pt;
                padding: 5px;
            }}
            QToolButton:hover {{
                border-color: #3498db;
                background-color: {hover_bg};
            }}
            QToolButton:checked {{
                border-color: #2ecc71;
                border-width: 3px;
                background-color: {checked_bg};
            }}
        """)
        
        # クリック時の処理
        btn.clicked.connect(lambda checked: self._on_background_selected(bg_id, bg_info))
        
        return btn
    
    def _on_background_selected(self, bg_id: str, bg_info: Dict[str, str]):
        """背景が選択された時の処理"""
        self.selected_bg_id = bg_id
        self.custom_bg_image = None  # カスタム画像をクリア
        
        # カスタムプレビューを非表示
        self.custom_preview_label.setVisible(False)
        self.custom_filename_label.setVisible(False)
        
        # シグナルを発火
        self.background_selected.emit(
            bg_id,
            bg_info["description"],
            bg_info["image"] if Path(bg_info["image"]).exists() else ""
        )
    
    def _upload_custom_background(self):
        """カスタム背景画像をアップロード"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "背景画像を選択",
            "",
            "画像ファイル (*.png *.jpg *.jpeg *.webp)"
        )
        
        if file_path:
            self.custom_bg_image = file_path
            self.selected_bg_id = "custom"
            
            # すべてのプリセットボタンの選択を解除
            for btn in self.button_group.buttons():
                btn.setChecked(False)
            
            # カスタム背景プレビューを表示
            pixmap = QPixmap(file_path)
            self.custom_preview_label.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.custom_preview_label.setVisible(True)
            
            # ファイル名を表示
            filename = Path(file_path).name
            self.custom_filename_label.setText(f"選択中: {filename}")
            self.custom_filename_label.setVisible(True)
            
            # カスタム背景用の説明を生成
            description = f"custom background from uploaded image"
            
            # シグナルを発火
            self.background_selected.emit("custom", description, file_path)
            
            print(f"[INFO] カスタム背景画像を選択: {file_path}")
    
    def get_selected_background(self) -> tuple:
        """選択されている背景情報を取得
        
        Returns:
            (bg_id, description, image_path)
        """
        if self.custom_bg_image:
            return ("custom", "custom background", self.custom_bg_image)
        else:
            bg_info = self.background_presets[self.selected_bg_id]
            return (
                self.selected_bg_id,
                bg_info["description"],
                bg_info["image"] if Path(bg_info["image"]).exists() else ""
            )
    
    def set_selected_background(self, bg_id: str):
        """プログラムで背景を選択"""
        if bg_id in self.background_presets:
            self.selected_bg_id = bg_id
            
            # 対応するボタンをチェック
            for i, (bid, _) in enumerate(self.background_presets.items()):
                if bid == bg_id:
                    btn = self.button_group.buttons()[i]
                    btn.setChecked(True)
                    break


