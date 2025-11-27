"""Gallery view widget"""

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QScrollArea, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QPixmap
from PIL import Image
from io import BytesIO
from typing import List, Optional
from pathlib import Path
import subprocess
import sys
import shutil

# 動画再生用（オプション）
try:
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PySide6.QtMultimediaWidgets import QVideoWidget
    VIDEO_PLAYBACK_AVAILABLE = True
except ImportError:
    VIDEO_PLAYBACK_AVAILABLE = False
    print("[Warning] QtMultimedia not available, video preview will use thumbnail")


class GalleryView(QWidget):
    """結果ギャラリービュー"""
    
    image_selected = Signal(Image.Image, int)  # 画像、インデックス

    def __init__(self, parent=None):
        super().__init__(parent)
        self.images: List[Image.Image] = []
        self.metadata = {}
        self.selected_index = -1
        self.video_path: Optional[str] = None  # 生成された動画のパス
        self.media_player: Optional['QMediaPlayer'] = None  # 動画プレイヤー
        self.video_widget: Optional['QVideoWidget'] = None  # 動画表示ウィジェット
        self.audio_output = None  # オーディオ出力
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
        self.video_path = None
        self._update_display()
    
    def set_video(self, video_path: str):
        """動画を設定してプレビューを表示"""
        self.video_path = video_path
        self._update_display()
    
    def get_video_path(self) -> Optional[str]:
        """動画パスを取得"""
        return self.video_path

    def _update_display(self):
        """表示を更新"""
        # 既存のウィジェットを削除
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

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
            select_btn.setStyleSheet(BUTTON_STYLE)
            select_btn.clicked.connect(lambda checked, idx=i, image=img: self._on_image_clicked(image, idx))
            container_layout.addWidget(select_btn)

            self.grid_layout.addWidget(container, row, col)
        
        # 動画プレビューを表示（画像の後に追加）
        if self.video_path and Path(self.video_path).exists():
            video_row = (len(self.images) + 1) // 2
            
            # 動画コンテナを作成
            video_container = QWidget()
            video_layout = QVBoxLayout(video_container)
            video_layout.setContentsMargins(5, 5, 5, 5)
            
            # 動画再生ウィジェットを作成
            if VIDEO_PLAYBACK_AVAILABLE:
                # QVideoWidgetで動画を再生
                self.video_widget = QVideoWidget()
                self.video_widget.setMinimumSize(400, 300)
                self.video_widget.setStyleSheet("""
                    QVideoWidget {
                        background-color: #1a1a2e;
                        border-radius: 10px;
                    }
                """)
                
                # メディアプレイヤーを作成
                self.media_player = QMediaPlayer()
                self.audio_output = QAudioOutput()
                self.media_player.setAudioOutput(self.audio_output)
                self.media_player.setVideoOutput(self.video_widget)
                
                # 動画をセット
                self.media_player.setSource(QUrl.fromLocalFile(self.video_path))
                
                # ループ再生のため、終了時に再度再生
                self.media_player.mediaStatusChanged.connect(self._on_media_status_changed)
                
                # 自動再生開始
                self.media_player.play()
                
                video_layout.addWidget(self.video_widget)
            else:
                # QtMultimediaが利用できない場合はサムネイル表示
                video_label = QLabel()
                video_label.setAlignment(Qt.AlignCenter)
                
                thumbnail = self._get_video_thumbnail(self.video_path)
                if thumbnail:
                    scaled_thumbnail = thumbnail.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    video_label.setPixmap(scaled_thumbnail)
                else:
                    video_label.setStyleSheet("""
                        QLabel {
                            background-color: #2c3e50;
                            border-radius: 10px;
                            padding: 20px;
                            min-height: 200px;
                            min-width: 300px;
                            color: white;
                            font-size: 14pt;
                            font-weight: bold;
                        }
                    """)
                    video_label.setText(f"動画生成完了\n\n{Path(self.video_path).name}")
                
                video_layout.addWidget(video_label)
            
            # 動画情報ラベル
            info_label = QLabel(f"動画: {Path(self.video_path).name}")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("font-size: 10pt; color: #666;")
            video_layout.addWidget(info_label)
            
            # ボタンレイアウト
            btn_layout = QHBoxLayout()
            
            # 再生/停止ボタン
            if VIDEO_PLAYBACK_AVAILABLE:
                self.play_pause_btn = QPushButton("一時停止")
                self.play_pause_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        font-weight: bold;
                        border-radius: 5px;
                        padding: 8px 16px;
                    }
                    QPushButton:hover {
                        background-color: #2ecc71;
                    }
                """)
                self.play_pause_btn.clicked.connect(self._toggle_play_pause)
                btn_layout.addWidget(self.play_pause_btn)
            else:
                play_btn = QPushButton("再生")
                play_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        font-weight: bold;
                        border-radius: 5px;
                        padding: 8px 16px;
                    }
                    QPushButton:hover {
                        background-color: #2ecc71;
                    }
                """)
                play_btn.clicked.connect(self._play_video)
                btn_layout.addWidget(play_btn)
            
            # 保存ボタン
            save_btn = QPushButton("保存")
            save_btn.setStyleSheet(BUTTON_STYLE)
            save_btn.clicked.connect(self._save_video)
            btn_layout.addWidget(save_btn)
            
            video_layout.addLayout(btn_layout)
            
            # 動画コンテナを追加（2列分の幅を使用）
            self.grid_layout.addWidget(video_container, video_row, 0, 1, 2)
    
    def _on_image_clicked(self, image: Image.Image, index: int):
        """画像がクリックされた時"""
        self.selected_index = index
        self.image_selected.emit(image, index)
    
    def _get_video_thumbnail(self, video_path: str) -> Optional[QPixmap]:
        """動画のサムネイル（最初のフレーム）を取得"""
        try:
            import cv2
            
            # 動画を開く
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"[Video] 動画を開けませんでした: {video_path}")
                return None
            
            # 最初のフレームを取得
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                print(f"[Video] フレームを読み取れませんでした")
                return None
            
            # BGRからRGBに変換
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # PIL Imageに変換
            pil_image = Image.fromarray(frame_rgb)
            
            # QPixmapに変換
            return self._pil_to_pixmap(pil_image)
        
        except ImportError:
            print("[Video] OpenCV (cv2) がインストールされていません")
            return None
        except Exception as e:
            print(f"[Video] サムネイル取得エラー: {e}")
            return None
    
    def _on_media_status_changed(self, status):
        """メディアステータス変更時の処理（ループ再生用）"""
        if VIDEO_PLAYBACK_AVAILABLE and self.media_player:
            if status == QMediaPlayer.MediaStatus.EndOfMedia:
                # 動画終了時に先頭から再度再生（ループ）
                self.media_player.setPosition(0)
                self.media_player.play()
    
    def _toggle_play_pause(self):
        """再生/一時停止を切り替え"""
        if VIDEO_PLAYBACK_AVAILABLE and self.media_player:
            if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.media_player.pause()
                if hasattr(self, 'play_pause_btn'):
                    self.play_pause_btn.setText("再生")
            else:
                self.media_player.play()
                if hasattr(self, 'play_pause_btn'):
                    self.play_pause_btn.setText("一時停止")
    
    def _play_video(self):
        """動画を外部プレイヤーで再生"""
        if self.video_path and Path(self.video_path).exists():
            try:
                # OSに応じてデフォルトのプレイヤーで開く
                if sys.platform == 'win32':
                    subprocess.run(['start', '', self.video_path], shell=True)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', self.video_path])
                else:
                    subprocess.run(['xdg-open', self.video_path])
                print(f"[Video] 動画を再生: {self.video_path}")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"動画の再生に失敗しました:\n{e}")
    
    def _save_video(self):
        """動画を保存"""
        if self.video_path and Path(self.video_path).exists():
            # 保存先を選択
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "動画を保存",
                f"fashion_video.mp4",
                "MP4ファイル (*.mp4)"
            )
            
            if save_path:
                try:
                    # ファイルをコピー
                    shutil.copy2(self.video_path, save_path)
                    QMessageBox.information(
                        self,
                        "保存完了",
                        f"動画を保存しました:\n{save_path}"
                    )
                    print(f"[Video] 動画を保存: {save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "エラー", f"保存に失敗しました:\n{e}")

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


