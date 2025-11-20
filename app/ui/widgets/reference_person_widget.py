"""Reference person upload widget"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from pathlib import Path
from typing import Optional
from PIL import Image


class ReferencePersonWidget(QWidget):
    """参考人物画像ウィジェット
    
    参考にする人物の画像をアップロードし、その人物に服を着せます
    """
    
    person_set = Signal(str, str)  # image_path, name
    person_cleared = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_person_image: Optional[str] = None
        self._setup_ui()
    
    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        
        # タイトル
        title_label = QLabel("👤 参考人物画像")
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 5px;")
        layout.addWidget(title_label)
        
        # 説明
        info_label = QLabel(
            "人物の画像を指定すると、その人物に服を着せた画像を生成します。\n"
            "指定しない場合は、新しいモデルが生成されます。\n\n"
            "📌 参考人物を指定した場合、モデル属性（性別・年代等）は無視されます。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 9pt; padding: 5px;")
        layout.addWidget(info_label)
        
        # プレビューエリア
        self.preview_label = QLabel("参考画像なし")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(150)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 5px;
                background-color: #f8f9fa;
                color: #999;
            }
        """)
        layout.addWidget(self.preview_label)
        
        # ボタン
        btn_layout = QHBoxLayout()
        
        # アップロードボタン
        self.upload_btn = QPushButton("📁 人物画像を選択")
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.upload_btn.clicked.connect(self._upload_person_image)
        btn_layout.addWidget(self.upload_btn)
        
        # クリアボタン
        self.clear_btn = QPushButton("✕ クリア")
        self.clear_btn.setEnabled(False)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:disabled {
                background-color: #ecf0f1;
                color: #bdc3c7;
            }
        """)
        self.clear_btn.clicked.connect(self._clear_person_image)
        btn_layout.addWidget(self.clear_btn)
        
        layout.addLayout(btn_layout)
        
        # 注意事項
        note_label = QLabel(
            "💡 ヒント:\n"
            "・全身が写っている画像が最適です\n"
            "・顔がはっきり見える画像を使用\n"
            "・背景がシンプルな画像を推奨"
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet("""
            QLabel {
                background-color: #fffacd;
                border: 1px solid #f0e68c;
                border-radius: 4px;
                padding: 8px;
                font-size: 8pt;
                color: #666;
            }
        """)
        layout.addWidget(note_label)
        
        layout.addStretch()
    
    def _upload_person_image(self):
        """人物画像をアップロード"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "参考人物の画像を選択",
            "",
            "画像ファイル (*.png *.jpg *.jpeg *.webp)"
        )
        
        if file_path:
            try:
                # 画像を確認
                img = Image.open(file_path)
                
                # プレビューを表示
                pixmap = QPixmap(file_path)
                scaled_pixmap = pixmap.scaled(
                    200, 200,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
                self.preview_label.setStyleSheet("""
                    QLabel {
                        border: 2px solid #9b59b6;
                        border-radius: 5px;
                        background-color: white;
                    }
                """)
                
                # 状態を更新
                self.current_person_image = file_path
                self.clear_btn.setEnabled(True)
                
                # シグナルを発火
                person_name = Path(file_path).stem
                self.person_set.emit(file_path, person_name)
                
                print(f"[Reference Person] 参考人物画像を設定: {file_path}")
            
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "エラー",
                    f"画像の読み込みに失敗しました:\n{str(e)}"
                )
    
    def _clear_person_image(self):
        """人物画像をクリア"""
        self.current_person_image = None
        self.preview_label.clear()
        self.preview_label.setText("参考画像なし")
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 5px;
                background-color: #f8f9fa;
                color: #999;
            }
        """)
        self.clear_btn.setEnabled(False)
        
        # シグナルを発火
        self.person_cleared.emit()
        
        print("[Reference Person] 参考人物画像をクリア")
    
    def get_person_image_path(self) -> Optional[str]:
        """参考人物画像のパスを取得"""
        return self.current_person_image
    
    def has_person_image(self) -> bool:
        """参考人物画像が設定されているか"""
        return self.current_person_image is not None

