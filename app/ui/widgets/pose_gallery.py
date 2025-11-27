"""Pose gallery widget for visual pose selection"""

from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QPushButton,
    QToolButton,
    QLabel,
    QVBoxLayout,
    QSizePolicy,
    QFileDialog,
    QButtonGroup,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon
from pathlib import Path
from typing import Dict, Optional


class PoseGalleryWidget(QWidget):
    """ポーズギャラリーウィジェット
    
    プリセットポーズまたはカスタムポーズ画像を選択できる
    """
    
    pose_selected = Signal(str, str, str)  # pose_id, description, image_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_pose_id = "front"  # デフォルト選択
        self.custom_pose_image = None  # カスタムポーズ画像のパス
        
        # プリセットポーズの定義
        self.pose_presets = self._load_pose_presets()
        
        # ボタングループ（排他的選択のため）
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        self._setup_ui()
    
    def _load_pose_presets(self) -> Dict[str, Dict[str, str]]:
        """プリセットポーズ情報を読み込み"""
        base_path = Path(__file__).parent.parent.parent / "assets" / "poses"
        
        return {
            "front": {
                "name": "正面",
                "image": str(base_path / "front.png"),
                "description": "standing straight, facing camera, arms at sides, full body visible from head to feet",
                "emoji": ""
            },
            "side": {
                "name": "側面",
                "image": str(base_path / "side.png"),
                "description": "standing in profile view, side pose, full body visible",
                "emoji": ""
            },
            "walking": {
                "name": "歩行",
                "image": str(base_path / "walking.png"),
                "description": "walking naturally with one leg forward in motion, dynamic pose",
                "emoji": ""
            },
            "sitting": {
                "name": "座位",
                "image": str(base_path / "sitting.png"),
                "description": "sitting on a chair or bench with legs positioned naturally, full body visible including feet",
                "emoji": ""
            },
            "arms_crossed": {
                "name": "腕組み",
                "image": str(base_path / "arms_crossed.png"),
                "description": "standing with arms crossed, confident pose",
                "emoji": ""
            },
            "hands_on_hips": {
                "name": "腰に手",
                "image": str(base_path / "hands_on_hips.png"),
                "description": "standing with hands on hips, assertive pose",
                "emoji": ""
            },
            "casual": {
                "name": "カジュアル",
                "image": str(base_path / "casual.png"),
                "description": "relaxed casual pose, one hand in pocket",
                "emoji": ""
            },
            "professional": {
                "name": "フォーマル",
                "image": str(base_path / "professional.png"),
                "description": "professional formal pose, standing upright",
                "emoji": ""
            }
        }
    
    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # タイトル
        title_label = QLabel("ポーズを選択")
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title_label)
        
        # ギャラリーグリッド
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)  # 隙間を狭める
        
        # プリセットポーズボタンを配置（4列）
        for i, (pose_id, pose_info) in enumerate(self.pose_presets.items()):
            row = i // 4
            col = i % 4
            
            # ポーズボタンを作成
            btn = self._create_pose_button(pose_id, pose_info)
            grid_layout.addWidget(btn, row, col)
            
            # ボタングループに追加
            self.button_group.addButton(btn)
            
            # デフォルト選択
            if pose_id == self.selected_pose_id:
                btn.setChecked(True)
        
        layout.addLayout(grid_layout)
        
        # 統一デザインのボタンスタイル
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
        """
        
        # カスタムポーズアップロードボタン
        custom_btn = QPushButton("カスタムポーズ画像をアップロード")
        custom_btn.setStyleSheet(BUTTON_STYLE)
        custom_btn.clicked.connect(self._upload_custom_pose)
        layout.addWidget(custom_btn)
        
        layout.addStretch()
    
    def _create_pose_button(self, pose_id: str, pose_info: Dict[str, str]) -> QToolButton:
        """ポーズボタンを作成（画像の下にテキスト表示）"""
        btn = QToolButton()
        btn.setCheckable(True)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # アイコンの下にテキスト
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.setMinimumSize(110, 130)
        btn.setMaximumSize(140, 160)
        
        # ボタンの内容を設定
        image_path = pose_info["image"]
        name = pose_info["name"]
        
        # 画像が存在するか確認
        if Path(image_path).exists():
            btn.setIcon(QIcon(image_path))
            btn.setIconSize(QSize(90, 90))
        
        # テキスト設定
        btn.setText(name)
        
        # スタイル設定
        btn.setStyleSheet("""
            QToolButton {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
                font-size: 9pt;
                padding: 5px;
            }
            QToolButton:hover {
                border-color: #3498db;
                background-color: #f0f8ff;
            }
            QToolButton:checked {
                border-color: #2ecc71;
                border-width: 3px;
                background-color: #e8f8f5;
            }
        """)
        
        # クリック時の処理
        btn.clicked.connect(lambda checked: self._on_pose_selected(pose_id, pose_info))
        
        return btn
    
    def _on_pose_selected(self, pose_id: str, pose_info: Dict[str, str]):
        """ポーズが選択された時の処理"""
        self.selected_pose_id = pose_id
        self.custom_pose_image = None  # カスタム画像をクリア
        
        # シグナルを発火
        self.pose_selected.emit(
            pose_id,
            pose_info["description"],
            pose_info["image"] if Path(pose_info["image"]).exists() else ""
        )
    
    def _upload_custom_pose(self):
        """カスタムポーズ画像をアップロード"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "ポーズ画像を選択",
            "",
            "画像ファイル (*.png *.jpg *.jpeg *.webp)"
        )
        
        if file_path:
            self.custom_pose_image = file_path
            self.selected_pose_id = "custom"
            
            # すべてのプリセットボタンの選択を解除
            for btn in self.button_group.buttons():
                btn.setChecked(False)
            
            # MediaPipeでポーズを抽出
            description = self._extract_pose_description(file_path)
            
            # シグナルを発火
            self.pose_selected.emit("custom", description, file_path)
            
            print(f"[INFO] カスタムポーズ画像を選択: {file_path}")
            print(f"[INFO] 抽出されたポーズ: {description}")
    
    def _extract_pose_description(self, image_path: str) -> str:
        """MediaPipeを使用してポーズ説明を抽出"""
        try:
            from core.vton.pose_extractor import PoseExtractor
            
            extractor = PoseExtractor()
            pose_info = extractor.extract_pose(image_path)
            
            if pose_info and pose_info.get('description'):
                return pose_info['description']
            else:
                # ポーズが検出できない場合はデフォルト
                return "custom pose from uploaded image, natural standing position"
        
        except Exception as e:
            print(f"[WARN] ポーズ抽出に失敗: {e}")
            return "custom pose from uploaded image"
    
    def get_selected_pose(self) -> tuple:
        """選択されているポーズ情報を取得
        
        Returns:
            (pose_id, description, image_path)
        """
        if self.custom_pose_image:
            return ("custom", "custom pose", self.custom_pose_image)
        else:
            pose_info = self.pose_presets[self.selected_pose_id]
            return (
                self.selected_pose_id,
                pose_info["description"],
                pose_info["image"] if Path(pose_info["image"]).exists() else ""
            )
    
    def set_selected_pose(self, pose_id: str):
        """プログラムでポーズを選択"""
        if pose_id in self.pose_presets:
            self.selected_pose_id = pose_id
            
            # 対応するボタンをチェック
            for i, (pid, _) in enumerate(self.pose_presets.items()):
                if pid == pose_id:
                    btn = self.button_group.buttons()[i]
                    btn.setChecked(True)
                    break

