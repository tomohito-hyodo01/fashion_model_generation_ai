"""Main application window"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QGroupBox,
    QFileDialog,
    QMessageBox,
    QProgressBar,
    QGridLayout,
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPixmap
from pathlib import Path
from typing import List, Optional, Dict
from PIL import Image
import asyncio

from models.clothing_item import ClothingItem
from models.model_attributes import ModelAttributes
from models.generation_config import GenerationConfig
from core.adapters.openai_adapter import OpenAIAdapter
from core.adapters.stability_adapter import StabilityAdapter
from core.adapters.vertex_adapter import VertexAdapter
from core.adapters.gemini_imagen_adapter import GeminiImagenAdapter
from core.pipeline.generate_service import GenerateService
from core.vton.fidelity_check import FidelityChecker
from utils.api_key_manager import APIKeyManager
from utils.config_manager import ConfigManager
from ui.widgets.garment_slot import GarmentSlotWidget
from ui.widgets.gallery_view import GalleryView
from ui.widgets.pose_gallery import PoseGalleryWidget
from ui.widgets.background_gallery import BackgroundGalleryWidget
from ui.widgets.chat_refinement import ChatRefinementWidget
from ui.widgets.history_panel import HistoryPanel
from ui.widgets.video_generator_panel import VideoGeneratorPanel
from ui.widgets.reference_person_widget import ReferencePersonWidget


class GenerationWorker(QThread):
    """生成処理ワーカースレッド"""

    progress_updated = Signal(int, str)
    generation_completed = Signal(list, dict)
    generation_failed = Signal(str)

    def __init__(self, service, garments, model_attrs, config, mode="variety", multi_angle_generator=None):
        super().__init__()
        self.service = service
        self.garments = garments
        self.model_attrs = model_attrs
        self.config = config
        self.mode = mode  # variety or angle
        self.multi_angle_generator = multi_angle_generator
        self._is_running = True

    def run(self):
        """バックグラウンドで実行"""
        try:
            import threading
            import time
            
            # 現在の進捗と目標進捗を管理
            self.current_progress = 0
            self.target_progress = 0
            self.current_message = "準備中..."
            self.smooth_update_running = True
            
            # 滑らかな進捗更新スレッド
            def smooth_progress_updater():
                """進捗を滑らかに更新"""
                while self.smooth_update_running:
                    if self.current_progress < self.target_progress:
                        # 目標に向かって徐々に増加
                        self.current_progress = min(
                            self.current_progress + 1,
                            self.target_progress
                        )
                        self.progress_updated.emit(self.current_progress, self.current_message)
                    time.sleep(0.1)  # 0.1秒ごとに1%ずつ増加
            
            # 滑らか更新スレッドを開始
            smooth_thread = threading.Thread(target=smooth_progress_updater, daemon=True)
            smooth_thread.start()
            
            # 初期進捗: 0%から段階的に開始
            self.target_progress = 0
            self.current_message = "準備中..."
            self.progress_updated.emit(0, "準備中...")
            time.sleep(0.1)
            
            # 進捗コールバック関数を定義
            def progress_callback(step: str, percentage: int):
                """進捗を更新するコールバック"""
                if self._is_running:
                    self.target_progress = percentage
                    self.current_message = step
            
            # 5%: 初期化
            self.target_progress = 5
            self.current_message = "初期化しています..."
            time.sleep(0.3)

            # asyncioイベントループを実行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # サービスに進捗コールバックを渡す
            self.service.progress_callback = progress_callback

            # 生成モードに応じて処理を分岐
            if self.mode == "angle" and self.multi_angle_generator:
                # マルチアングル生成
                from core.pipeline.multi_angle_generator import MultiAngleGenerator
                
                angles = self.multi_angle_generator.get_angle_configurations(self.config.num_outputs)
                print(f"[Multi-Angle] モード: {len(angles)}つの角度から生成")
                
                images, metadata = loop.run_until_complete(
                    self.multi_angle_generator.generate_multi_angle(
                        self.service,
                        self.garments,
                        self.model_attrs,
                        self.config,
                        angles,
                        progress_callback
                    )
                )
            else:
                # 通常生成（バリエーション）
                images, metadata = loop.run_until_complete(
                    self.service.run(self.garments, self.model_attrs, self.config)
                )
            
            # 最終進捗
            self.smooth_update_running = False
            self.progress_updated.emit(100, "生成が完了しました")
            self.generation_completed.emit(images, metadata)

        except Exception as e:
            self._is_running = False
            self.smooth_update_running = False
            self.generation_failed.emit(str(e))

        finally:
            loop.close()


class ChatRefinementWorker(QThread):
    """チャット修正処理ワーカースレッド"""

    progress_updated = Signal(int, str)
    refinement_completed = Signal(Image.Image, str)  # 画像, AI応答
    refinement_failed = Signal(str)

    def __init__(self, chat_service, instruction, generate_service, garments, model_attrs, config, conversation_history):
        super().__init__()
        self.chat_service = chat_service
        self.instruction = instruction
        self.generate_service = generate_service
        self.garments = garments
        self.model_attrs = model_attrs
        self.config = config
        self.conversation_history = conversation_history

    def run(self):
        """バックグラウンドで実行"""
        try:
            import asyncio
            
            # 進捗コールバック
            def progress_callback(step: str, percentage: int):
                self.progress_updated.emit(percentage, step)
            
            # asyncioイベントループを実行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # サービスに進捗コールバックを渡す
            self.generate_service.progress_callback = progress_callback
            
            # チャット修正を実行
            images, ai_response, metadata = loop.run_until_complete(
                self.chat_service.refine_image(
                    self.instruction,
                    self.generate_service,
                    self.garments,
                    self.model_attrs,
                    self.config,
                    self.conversation_history,
                    progress_callback
                )
            )
            
            if images and len(images) > 0:
                self.refinement_completed.emit(images[0], ai_response)
            else:
                self.refinement_failed.emit("画像の生成に失敗しました")

        except Exception as e:
            self.refinement_failed.emit(str(e))
        finally:
            loop.close()


class VideoGenerationWorker(QThread):
    """動画生成処理ワーカースレッド"""

    progress_updated = Signal(int, str)
    video_generated = Signal(str, dict)  # video_path, metadata
    video_generation_failed = Signal(str)

    def __init__(self, adapter, image, settings, output_path):
        super().__init__()
        self.adapter = adapter
        self.image = image
        self.settings = settings
        self.output_path = output_path

    def run(self):
        """バックグラウンドで実行"""
        try:
            # 進捗コールバック
            def progress_callback(step: str, percentage: int):
                self.progress_updated.emit(percentage, step)
            
            # 動画を生成
            video_url, metadata = self.adapter.generate_video(
                image=self.image,
                duration=self.settings["duration"],
                resolution=self.settings["resolution"],
                prompt=self.settings.get("prompt"),
                progress_callback=progress_callback
            )
            
            # 動画をダウンロード
            progress_callback("動画をダウンロード中...", 90)
            success = self.adapter.download_video(video_url, self.output_path)
            
            if success:
                self.video_generated.emit(self.output_path, metadata)
            else:
                self.video_generation_failed.emit("動画のダウンロードに失敗しました")

        except Exception as e:
            self.video_generation_failed.emit(str(e))


class FashnTryonWorker(QThread):
    """FASHN Virtual Try-On処理ワーカースレッド"""

    progress_updated = Signal(int, str)
    generation_completed = Signal(list, dict)
    generation_failed = Signal(str)

    def __init__(self, adapter, person_image_path, garment_image_path, category, num_samples):
        super().__init__()
        self.adapter = adapter
        self.person_image_path = person_image_path
        self.garment_image_path = garment_image_path
        self.category = category
        self.num_samples = num_samples

    def run(self):
        """バックグラウンドで実行"""
        try:
            # 進捗コールバック
            def progress_callback(step: str, percentage: int):
                self.progress_updated.emit(percentage, step)
            
            # 画像を読み込み
            progress_callback("画像を読み込み中...", 5)
            person_image = Image.open(self.person_image_path)
            garment_image = Image.open(self.garment_image_path)
            
            # FASHN Virtual Try-Onを実行
            images, metadata = self.adapter.virtual_tryon(
                person_image=person_image,
                garment_image=garment_image,
                category=self.category,
                garment_photo_type="flat-lay",
                mode="quality",
                num_samples=self.num_samples,
                progress_callback=progress_callback
            )
            
            progress_callback("完了", 100)
            
            # 結果を返す
            self.generation_completed.emit(images, metadata)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.generation_failed.emit(str(e))


class MainWindow(QMainWindow):
    """メインウィンドウ"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virtual Fashion Try-On")
        self.setMinimumSize(1200, 800)

        # 設定とAPIキー管理
        self.config_manager = ConfigManager()
        self.api_key_manager = APIKeyManager()
        
        # 履歴管理
        from core.history.history_manager import HistoryManager
        self.history_manager = HistoryManager()

        # 衣類アイテムのリスト
        self.garments: List[ClothingItem] = []
        
        # 参考人物画像（オプション）
        self.reference_person_image: Optional[str] = None
        self.reference_person_name: str = ""

        # ワーカースレッド
        self.worker: Optional[GenerationWorker] = None
        
        # 選択されたポーズと背景の情報
        self.selected_pose_info = ("front", "standing straight, facing camera", "")
        self.selected_background_info = ("white", "plain solid white background", "")
        
        # 生成モード（variety: 種類違い, angle: 角度違い）
        self.generation_mode = "variety"
        
        # 最後に生成したパラメータ（チャット修正用）
        self.last_generation_params = None

        # UIを構築
        self._setup_ui()
        
        # メニューバーを構築
        self._setup_menubar()

        # APIキーの確認
        self._check_api_keys()

    def _setup_ui(self):
        """UIをセットアップ"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # トップエリア（参考人物 + 衣類画像 + モデル属性）
        top_layout = QHBoxLayout()

        # 左: 参考人物画像
        reference_person_group = self._create_reference_person_group()
        top_layout.addWidget(reference_person_group, stretch=1)

        # 中央: 衣類画像アップロード
        upload_group = self._create_upload_group()
        top_layout.addWidget(upload_group, stretch=1)

        # 右: モデル属性選択
        model_group = self._create_model_attributes_group()
        top_layout.addWidget(model_group, stretch=2)

        main_layout.addLayout(top_layout)

        # 中段: 生成設定
        settings_group = self._create_generation_settings_group()
        main_layout.addWidget(settings_group)

        # 進捗バー
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 5px;
                text-align: center;
                background-color: #ecf0f1;
                font-weight: bold;
                font-size: 12pt;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # 下段: 履歴 + 結果ギャラリー + チャット + 動画生成（4カラム）
        bottom_layout = QHBoxLayout()
        
        # 左: 履歴パネル
        history_group = self._create_history_group()
        bottom_layout.addWidget(history_group, stretch=1)
        
        # 中央左: 結果ギャラリー
        gallery_group = self._create_gallery_group()
        bottom_layout.addWidget(gallery_group, stretch=2)
        
        # 中央右: チャット修正パネル
        chat_group = self._create_chat_group()
        bottom_layout.addWidget(chat_group, stretch=1)
        
        # 右: 動画生成パネル
        video_group = self._create_video_group()
        bottom_layout.addWidget(video_group, stretch=1)
        
        main_layout.addLayout(bottom_layout)

    def _create_reference_person_group(self) -> QGroupBox:
        """参考人物グループを作成"""
        group = QGroupBox("参考人物")
        layout = QVBoxLayout()
        
        # 参考人物ウィジェット
        self.reference_person_widget = ReferencePersonWidget()
        self.reference_person_widget.person_set.connect(self._on_reference_person_set)
        self.reference_person_widget.person_cleared.connect(self._on_reference_person_cleared)
        layout.addWidget(self.reference_person_widget)
        
        group.setLayout(layout)
        return group
    
    def _on_reference_person_set(self, image_path: str, name: str):
        """参考人物が設定された時"""
        self.reference_person_image = image_path
        self.reference_person_name = name
        print(f"[Reference Person] 参考人物を設定: {name}")
        self.statusBar().showMessage(f"参考人物を設定しました: {name}", 3000)
    
    def _on_reference_person_cleared(self):
        """参考人物がクリアされた時"""
        self.reference_person_image = None
        self.reference_person_name = ""
        print("[Reference Person] 参考人物をクリア")
        self.statusBar().showMessage("参考人物をクリアしました", 3000)
    
    def _create_upload_group(self) -> QGroupBox:
        """画像アップロードグループを作成"""
        group = QGroupBox("衣類画像")
        layout = QVBoxLayout()

        # アップロードボタン
        upload_btn = QPushButton("+ 画像を追加")
        upload_btn.clicked.connect(self._add_garment_image)
        layout.addWidget(upload_btn)

        # 衣類スロット表示エリア
        self.garment_slots_layout = QVBoxLayout()
        layout.addLayout(self.garment_slots_layout)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_model_attributes_group(self) -> QGroupBox:
        """モデル属性選択グループを作成"""
        from PySide6.QtWidgets import QScrollArea, QTabWidget
        
        group = QGroupBox("モデル属性")
        main_layout = QVBoxLayout()

        # タブウィジェット（基本属性・ポーズ・背景）
        tab_widget = QTabWidget()
        
        # === タブ1: 基本属性 ===
        basic_tab = QWidget()
        basic_layout = QGridLayout(basic_tab)

        # 性別
        basic_layout.addWidget(QLabel("性別:"), 0, 0)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["女性", "男性"])
        basic_layout.addWidget(self.gender_combo, 0, 1)

        # 年代
        basic_layout.addWidget(QLabel("年代:"), 1, 0)
        self.age_combo = QComboBox()
        self.age_combo.addItems(["10代", "20代", "30代", "40代", "50代以上"])
        self.age_combo.setCurrentText("20代")
        basic_layout.addWidget(self.age_combo, 1, 1)

        # 地域/出身
        basic_layout.addWidget(QLabel("地域:"), 2, 0)
        self.ethnicity_combo = QComboBox()
        self.ethnicity_combo.addItems(["アジア", "ヨーロッパ", "アフリカ", "南北アメリカ", "オセアニア", "混合"])
        basic_layout.addWidget(self.ethnicity_combo, 2, 1)

        # 体型
        basic_layout.addWidget(QLabel("体型:"), 3, 0)
        self.body_type_combo = QComboBox()
        self.body_type_combo.addItems(["スリム", "標準", "アスリート", "ぽっちゃり"])
        self.body_type_combo.setCurrentText("標準")
        basic_layout.addWidget(self.body_type_combo, 3, 1)

        basic_layout.setRowStretch(4, 1)  # 余白
        tab_widget.addTab(basic_tab, "基本")
        
        # === タブ2: ポーズ ===
        pose_tab = QWidget()
        pose_layout = QVBoxLayout(pose_tab)
        
        # ポーズギャラリー
        self.pose_gallery = PoseGalleryWidget()
        self.pose_gallery.pose_selected.connect(self._on_pose_selected)
        
        # スクロールエリアに配置
        pose_scroll = QScrollArea()
        pose_scroll.setWidget(self.pose_gallery)
        pose_scroll.setWidgetResizable(True)
        pose_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        pose_layout.addWidget(pose_scroll)
        
        tab_widget.addTab(pose_tab, "ポーズ")
        
        # === タブ3: 背景 ===
        bg_tab = QWidget()
        bg_layout = QVBoxLayout(bg_tab)
        
        # 背景ギャラリー
        self.background_gallery = BackgroundGalleryWidget()
        self.background_gallery.background_selected.connect(self._on_background_selected)
        
        # スクロールエリアに配置
        bg_scroll = QScrollArea()
        bg_scroll.setWidget(self.background_gallery)
        bg_scroll.setWidgetResizable(True)
        bg_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        bg_layout.addWidget(bg_scroll)
        
        tab_widget.addTab(bg_tab, "背景")
        
        main_layout.addWidget(tab_widget)
        group.setLayout(main_layout)
        return group
    
    def _on_pose_selected(self, pose_id: str, description: str, image_path: str):
        """ポーズが選択された時の処理"""
        self.selected_pose_info = (pose_id, description, image_path)
        print(f"[INFO] ポーズ選択: {pose_id} - {description}")
    
    def _on_background_selected(self, bg_id: str, description: str, image_path: str):
        """背景が選択された時の処理"""
        self.selected_background_info = (bg_id, description, image_path)
        print(f"[INFO] 背景選択: {bg_id} - {description}")

    def _create_generation_settings_group(self) -> QGroupBox:
        """生成設定グループを作成"""
        from PySide6.QtWidgets import QRadioButton, QButtonGroup
        
        group = QGroupBox("生成設定")
        layout = QVBoxLayout()
        
        # 第1行: サイズと枚数
        row1_layout = QHBoxLayout()
        
        # サイズ
        row1_layout.addWidget(QLabel("サイズ:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(["1024x1024", "1024x1792", "1792x1024"])
        row1_layout.addWidget(self.size_combo)
        
        row1_layout.addSpacing(20)
        
        # 出力枚数
        row1_layout.addWidget(QLabel("枚数:"))
        self.num_outputs_spin = QSpinBox()
        self.num_outputs_spin.setRange(1, 4)
        self.num_outputs_spin.setValue(1)
        row1_layout.addWidget(self.num_outputs_spin)
        
        row1_layout.addStretch()
        layout.addLayout(row1_layout)
        
        # 第2行: 生成モード選択
        row2_layout = QHBoxLayout()
        row2_layout.addWidget(QLabel("生成モード:"))
        
        # ラジオボタングループ
        self.mode_button_group = QButtonGroup()
        
        self.variety_radio = QRadioButton("種類違い（バリエーション）")
        self.variety_radio.setChecked(True)
        self.variety_radio.toggled.connect(lambda checked: self._on_mode_changed("variety" if checked else None))
        self.mode_button_group.addButton(self.variety_radio)
        row2_layout.addWidget(self.variety_radio)
        
        self.angle_radio = QRadioButton("角度違い（マルチアングル）")
        self.angle_radio.toggled.connect(lambda checked: self._on_mode_changed("angle" if checked else None))
        self.mode_button_group.addButton(self.angle_radio)
        row2_layout.addWidget(self.angle_radio)
        
        row2_layout.addStretch()
        layout.addLayout(row2_layout)
        
        # 角度モード説明ラベル
        self.angle_mode_label = QLabel("💡 角度違いモード: 同じモデル・衣類で異なる角度から撮影した画像を生成します")
        self.angle_mode_label.setStyleSheet("color: #3498db; font-size: 9pt; padding: 5px;")
        self.angle_mode_label.setVisible(False)
        layout.addWidget(self.angle_mode_label)
        
        # 第3行: 生成ボタン
        row3_layout = QHBoxLayout()
        row3_layout.addStretch()
        
        self.generate_btn = QPushButton("生成開始")
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                font-size: 12pt;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.generate_btn.clicked.connect(self._start_generation)
        row3_layout.addWidget(self.generate_btn)
        
        row3_layout.addStretch()
        layout.addLayout(row3_layout)
        
        group.setLayout(layout)
        return group
    
    def _on_mode_changed(self, mode: Optional[str]):
        """生成モードが変更された時の処理"""
        if mode:
            self.generation_mode = mode
            self.angle_mode_label.setVisible(mode == "angle")
            print(f"[INFO] 生成モード変更: {mode}")

    def _create_gallery_group(self) -> QGroupBox:
        """結果ギャラリーグループを作成"""
        group = QGroupBox("生成結果")
        layout = QVBoxLayout()

        # ギャラリービュー
        self.gallery_view = GalleryView()
        self.gallery_view.image_selected.connect(self._on_gallery_image_selected)
        layout.addWidget(self.gallery_view)

        # ボタン
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save_results)
        btn_layout.addWidget(save_btn)

        clear_btn = QPushButton("クリア")
        clear_btn.clicked.connect(self._clear_results)
        btn_layout.addWidget(clear_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        group.setLayout(layout)
        return group
    
    def _create_history_group(self) -> QGroupBox:
        """履歴グループを作成"""
        group = QGroupBox("生成履歴")
        layout = QVBoxLayout()
        
        # 履歴パネル
        self.history_panel = HistoryPanel(self.history_manager)
        self.history_panel.history_selected.connect(self._on_history_selected)
        layout.addWidget(self.history_panel)
        
        group.setLayout(layout)
        return group
    
    def _create_chat_group(self) -> QGroupBox:
        """チャット修正グループを作成"""
        group = QGroupBox("チャットで修正")
        layout = QVBoxLayout()
        
        # チャットウィジェット
        self.chat_widget = ChatRefinementWidget()
        self.chat_widget.refinement_requested.connect(self._on_refinement_requested)
        layout.addWidget(self.chat_widget)
        
        group.setLayout(layout)
        return group
    
    def _create_video_group(self) -> QGroupBox:
        """動画生成グループを作成"""
        group = QGroupBox("動画生成")
        layout = QVBoxLayout()
        
        # 動画生成パネル
        self.video_panel = VideoGeneratorPanel()
        self.video_panel.video_generation_requested.connect(self._on_video_generation_requested)
        layout.addWidget(self.video_panel)
        
        group.setLayout(layout)
        return group
    
    def _on_history_selected(self, history_id: int, images: List[Image.Image], parameters: Dict):
        """履歴が選択された時"""
        # ギャラリーに画像を表示
        self.gallery_view.set_images(images, {"history_id": history_id})
        self.statusBar().showMessage(f"履歴ID {history_id} を読み込みました", 3000)
        
        print(f"[History] 履歴を読み込み: ID={history_id}, 画像数={len(images)}")
    
    def _on_gallery_image_selected(self, image: Image.Image, index: int):
        """ギャラリーで画像が選択された時"""
        if self.last_generation_params:
            # チャットウィジェットに画像とパラメータを設定
            self.chat_widget.set_current_image(image, self.last_generation_params)
            print(f"[INFO] 画像 {index+1} がチャット修正用に選択されました")
        
        # 動画生成パネルにも画像を設定
        self.video_panel.set_current_image(image)
        print(f"[INFO] 画像 {index+1} が動画生成用に選択されました")
    
    def _on_refinement_requested(self, instruction: str, context: Dict):
        """チャットで修正が要求された時"""
        print(f"[Chat] 修正要求: {instruction}")
        
        # 修正処理をバックグラウンドで実行
        self._start_chat_refinement(instruction, context)
    
    def _start_chat_refinement(self, instruction: str, context: Dict):
        """チャット修正を開始"""
        from core.pipeline.chat_refinement_service import ChatRefinementService
        
        # Gemini APIキーを取得
        gemini_key = self.api_key_manager.load_api_key("gemini")
        if not gemini_key:
            self.chat_widget.on_refinement_failed("Gemini APIキーが設定されていません")
            return
        
        # ChatRefinementServiceを作成
        chat_service = ChatRefinementService(gemini_key)
        
        # パラメータを復元
        params = context.get("params", {})
        if not params:
            self.chat_widget.on_refinement_failed("パラメータが見つかりません")
            return
        
        # ModelAttributesを再構築
        gender_map = {"女性": "female", "男性": "male"}
        age_map = {"10代": "10s", "20代": "20s", "30代": "30s", "40代": "40s", "50代以上": "50s+"}
        ethnicity_map = {
            "アジア": "asian", "ヨーロッパ": "european", "アフリカ": "african",
            "南北アメリカ": "american", "オセアニア": "oceanian", "混合": "mixed"
        }
        body_type_map = {"スリム": "slim", "標準": "standard", "アスリート": "athletic", "ぽっちゃり": "plus-size"}
        
        model_attrs_dict = params.get("model_attrs", {})
        model_attrs = ModelAttributes(
            gender=gender_map.get(model_attrs_dict.get("gender", "女性"), "female"),
            age_range=age_map.get(model_attrs_dict.get("age_range", "20代"), "20s"),
            ethnicity=ethnicity_map.get(model_attrs_dict.get("ethnicity", "アジア"), "asian"),
            body_type=body_type_map.get(model_attrs_dict.get("body_type", "標準"), "standard"),
            height="standard",
            pose=model_attrs_dict.get("pose", "front"),
            background=model_attrs_dict.get("background", "white"),
            custom_description=f"Pose: {model_attrs_dict.get('pose_description', '')}. Background: {model_attrs_dict.get('background_description', '')}"
        )
        
        # GenerationConfigを再構築
        config_dict = params.get("config", {})
        config = GenerationConfig(
            provider="gemini",
            quality="standard",
            size=config_dict.get("size", "1024x1024"),
            num_outputs=1
        )
        
        # Geminiアダプタを作成
        adapter = self._create_adapter("gemini")
        if not adapter:
            self.chat_widget.on_refinement_failed("Geminiアダプタの作成に失敗しました")
            return
        
        # GenerateServiceを作成
        from core.vton.fidelity_check import FidelityChecker
        fidelity_checker = FidelityChecker()
        generate_service = GenerateService(adapter, fidelity_checker)
        
        # 会話履歴を取得
        conversation_history = context.get("history", [])
        
        # ワーカースレッドで実行
        self.chat_worker = ChatRefinementWorker(
            chat_service,
            instruction,
            generate_service,
            params.get("garments", self.garments),
            model_attrs,
            config,
            conversation_history
        )
        self.chat_worker.progress_updated.connect(self._update_progress)
        self.chat_worker.refinement_completed.connect(self._on_chat_refinement_completed)
        self.chat_worker.refinement_failed.connect(self._on_chat_refinement_failed)
        
        # 進捗バーを表示
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.chat_worker.start()
    
    def _on_chat_refinement_completed(self, new_image: Image.Image, ai_response: str):
        """チャット修正完了時の処理"""
        self.progress_bar.setVisible(False)
        
        # チャットウィジェットに通知
        self.chat_widget.on_refinement_completed(new_image, ai_response)
        
        # ギャラリーに追加
        current_images = self.gallery_view.get_images()
        current_images.append(new_image)
        self.gallery_view.set_images(current_images, {})
        
        self.statusBar().showMessage("修正画像を生成しました", 3000)
    
    def _on_chat_refinement_failed(self, error_message: str):
        """チャット修正失敗時の処理"""
        self.progress_bar.setVisible(False)
        self.chat_widget.on_refinement_failed(error_message)
        self.statusBar().showMessage(f"修正に失敗: {error_message}", 5000)
    
    def _on_video_generation_requested(self, image: Image.Image, settings: Dict):
        """動画生成が要求された時"""
        print(f"[Video] 動画生成要求")
        print(f"  duration: {settings['duration']}秒")
        print(f"  resolution: {settings['resolution']}")
        
        # FASHN APIキーを取得
        fashn_key = self.api_key_manager.load_api_key("fashn")
        if not fashn_key:
            # デフォルトキーを使用
            fashn_key = "fa-uCRCpnOMl0uK-ylgH33BqyMDdtVyiEZ9SDRLo"
            print("[Video] デフォルトFASHN APIキーを使用")
        
        # FashnVideoAdapterを作成
        from core.adapters.fashn_video_adapter import FashnVideoAdapter
        adapter = FashnVideoAdapter(fashn_key)
        
        # 一時保存先を決定
        from datetime import datetime
        output_filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        temp_dir = Path.home() / "AppData" / "Local" / "VirtualFashionTryOn" / "videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(temp_dir / output_filename)
        
        # ワーカースレッドで実行
        self.video_worker = VideoGenerationWorker(
            adapter,
            image,
            settings,
            output_path
        )
        self.video_worker.progress_updated.connect(self._update_progress)
        self.video_worker.video_generated.connect(self._on_video_generated)
        self.video_worker.video_generation_failed.connect(self._on_video_generation_failed)
        
        # 進捗バーを表示
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.video_worker.start()
    
    def _on_video_generated(self, video_path: str, metadata: Dict):
        """動画生成完了時の処理"""
        self.progress_bar.setVisible(False)
        
        # 動画パネルに通知
        self.video_panel.on_video_generated(video_path)
        
        self.statusBar().showMessage(f"動画を生成しました: {Path(video_path).name}", 5000)
        
        print(f"[Video] 動画生成完了: {video_path}")
    
    def _on_video_generation_failed(self, error_message: str):
        """動画生成失敗時の処理"""
        self.progress_bar.setVisible(False)
        
        # 動画パネルに通知
        self.video_panel.on_video_generation_failed(error_message)
        
        QMessageBox.critical(self, "エラー", f"動画生成に失敗しました:\n{error_message}")
        
        print(f"[Video] 動画生成失敗: {error_message}")

    def _add_garment_image(self):
        """衣類画像を追加"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "衣類画像を選択", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )

        if file_path:
            try:
                # 衣類タイプを選択
                clothing_type = self._select_clothing_type()
                if not clothing_type:
                    return

                # 衣類画像を分析
                from core.vton.clothing_analyzer import ClothingAnalyzer
                analyzer = ClothingAnalyzer()
                
                try:
                    features = analyzer.analyze_clothing(file_path)
                    description = analyzer.generate_detailed_description(features, clothing_type)
                except Exception as analysis_error:
                    # 分析に失敗した場合はデフォルト値を使用
                    print(f"Warning: Failed to analyze image: {analysis_error}")
                    features = {"colors": [], "pattern": "solid", "texture": "medium"}
                    description = f"{clothing_type.lower()} garment"

                # ClothingItemを作成
                garment = ClothingItem(
                    image_path=file_path,
                    clothing_type=clothing_type,
                    colors=features.get("colors", []),
                    analyzed_description=description,
                )
                self.garments.append(garment)

                # スロットウィジェットを追加
                slot_widget = GarmentSlotWidget(garment)
                slot_widget.remove_requested.connect(
                    lambda g=garment: self._remove_garment(g)
                )
                self.garment_slots_layout.addWidget(slot_widget)
                
                # 成功メッセージ
                self.statusBar().showMessage(f"衣類画像を追加しました: {garment.display_name}", 3000)

            except Exception as e:
                QMessageBox.warning(self, "エラー", f"画像の追加に失敗しました:\n{str(e)}")

    def _select_clothing_type(self) -> Optional[str]:
        """衣類タイプを選択"""
        from PySide6.QtWidgets import QInputDialog

        # 日本語の選択肢
        types_jp = ["トップス", "ボトムス", "アウター", "ワンピース", "アクセサリー"]
        type_jp, ok = QInputDialog.getItem(
            self, "衣類タイプを選択", "タイプ:", types_jp, 0, False
        )
        
        if not ok:
            return None
        
        # 日本語 → 英語に変換
        type_map = {
            "トップス": "TOP",
            "ボトムス": "BOTTOM",
            "アウター": "OUTER",
            "ワンピース": "ONE_PIECE",
            "アクセサリー": "ACCESSORY"
        }
        
        return type_map.get(type_jp, "TOP")

    def _remove_garment(self, garment: ClothingItem):
        """衣類を削除"""
        if garment in self.garments:
            self.garments.remove(garment)
            
            # レイアウトから対応するウィジェットを削除
            for i in reversed(range(self.garment_slots_layout.count())):
                widget = self.garment_slots_layout.itemAt(i).widget()
                if widget and hasattr(widget, 'garment') and widget.garment == garment:
                    widget.deleteLater()
                    self.garment_slots_layout.removeWidget(widget)
                    break
            
            # ステータスバーにメッセージを表示
            self.statusBar().showMessage(f"衣類画像を削除しました: {garment.display_name}", 3000)

    def _start_generation(self):
        """画像生成を開始（固定フロー: Stability AI + Gemini 2.5 Flash Image）"""
        if not self.garments:
            QMessageBox.warning(self, "警告", "衣類画像を追加してください。")
            return

        # 日本語 → 英語のマッピング
        gender_map = {"女性": "female", "男性": "male"}
        age_map = {"10代": "10s", "20代": "20s", "30代": "30s", "40代": "40s", "50代以上": "50s+"}
        ethnicity_map = {
            "アジア": "asian",
            "ヨーロッパ": "european",
            "アフリカ": "african",
            "南北アメリカ": "american",
            "オセアニア": "oceanian",
            "混合": "mixed"
        }
        body_type_map = {"スリム": "slim", "標準": "standard", "アスリート": "athletic", "ぽっちゃり": "plus-size"}
        pose_map = {"正面": "front", "側面": "side", "歩行": "walking", "座位": "sitting"}
        background_map = {"白": "white", "透過": "transparent", "スタジオ": "studio", "ロケーション": "location"}

        # ポーズと背景の情報を取得
        pose_id, pose_description, pose_image = self.selected_pose_info
        bg_id, bg_description, bg_image = self.selected_background_info
        
        # モデル属性を取得（日本語 → 英語に変換）
        model_attrs = ModelAttributes(
            gender=gender_map.get(self.gender_combo.currentText(), "female"),
            age_range=age_map.get(self.age_combo.currentText(), "20s"),
            ethnicity=ethnicity_map.get(self.ethnicity_combo.currentText(), "asian"),
            body_type=body_type_map.get(self.body_type_combo.currentText(), "standard"),
            height="standard",
            pose=pose_id,  # ギャラリーから選択されたポーズID
            background=bg_id,  # ギャラリーから選択された背景ID
            custom_description=f"Pose: {pose_description}. Background: {bg_description}",
        )

        # 生成設定（Gemini固定）
        config = GenerationConfig(
            provider="gemini",
            quality="standard",
            size=self.size_combo.currentText(),
            num_outputs=self.num_outputs_spin.value(),
        )

        # 参考人物がある場合はFASHN Virtual Try-Onを使用、ない場合はGemini
        if self.reference_person_image:
            print(f"[MainWindow] 参考人物モード: FASHN Virtual Try-Onを使用")
            print(f"[MainWindow] モデル属性は無視されます（参考人物がベース）")
            adapter = "fashn_tryon"  # 特別なフラグ
        else:
            print(f"[MainWindow] 通常モード: Geminiを使用")
            # Gemini 2.5 Flash Imageアダプタを作成
            adapter = self._create_adapter("gemini")
            if not adapter:
                QMessageBox.warning(
                    self, 
                    "エラー", 
                    "Gemini APIキーが設定されていません。\n"
                    "設定 → APIキー設定から「gemini」のAPIキーを追加してください。"
                )
                return

        # 参考人物モードの場合は特別処理
        if adapter == "fashn_tryon":
            # FASHN Virtual Try-On モード
            print(f"[MainWindow] FASHN Virtual Try-On モード")
            
            # FASHN APIキーを取得
            fashn_key = self.api_key_manager.load_api_key("fashn")
            if not fashn_key:
                # デフォルトキー
                fashn_key = "fa-uCRCpnOMl0uK-ylgH33BqyMDdtVyiEZ9SDRLo"
                print("[MainWindow] デフォルトFASHN APIキーを使用")
            
            # FASHN Try-Onアダプターを作成
            from core.adapters.fashn_tryon_adapter import FashnTryonAdapter
            tryon_adapter = FashnTryonAdapter(fashn_key)
            
            # 衣類のカテゴリーを判定（最初の衣類のみ対応）
            if self.garments:
                first_garment = self.garments[0]
                category_map = {
                    "TOP": "tops",
                    "BOTTOM": "bottoms",
                    "ONE_PIECE": "one-pieces",
                    "OUTER": "tops",
                    "ACCESSORY": "tops"
                }
                category = category_map.get(first_garment.clothing_type, "auto")
                garment_path = first_garment.image_path
            else:
                QMessageBox.warning(self, "警告", "衣類画像を追加してください。")
                return
            
            print(f"[MainWindow] カテゴリー: {category}")
            
            # ワーカースレッドで実行
            self.tryon_worker = FashnTryonWorker(
                tryon_adapter,
                self.reference_person_image,
                garment_path,
                category,
                config.num_outputs
            )
            self.tryon_worker.progress_updated.connect(self._update_progress)
            self.tryon_worker.generation_completed.connect(self._on_generation_completed)
            self.tryon_worker.generation_failed.connect(self._on_generation_failed)
            
            # UIを更新
            self.generate_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            self.tryon_worker.start()
        else:
            # 通常のGemini生成
            # GenerateServiceを作成
            fidelity_checker = FidelityChecker()
            service = GenerateService(adapter, fidelity_checker)

            # マルチアングルジェネレーターを作成（角度違いモードの場合）
            multi_angle_generator = None
            if self.generation_mode == "angle":
                from core.pipeline.multi_angle_generator import MultiAngleGenerator
                multi_angle_generator = MultiAngleGenerator()

            # ワーカースレッドで実行
            self.worker = GenerationWorker(
                service, 
                self.garments, 
                model_attrs, 
                config,
                mode=self.generation_mode,
                multi_angle_generator=multi_angle_generator
            )
            self.worker.progress_updated.connect(self._update_progress)
            self.worker.generation_completed.connect(self._on_generation_completed)
            self.worker.generation_failed.connect(self._on_generation_failed)

            # UIを更新
            self.generate_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            self.worker.start()
    
    def _start_inpainting_generation(self, model_attrs, config):
        """参考人物+顔交換を使用した生成を開始"""
        print(f"[MainWindow] 参考人物モード: Gemini生成 + 顔交換")
        
        # Geminiアダプターを作成（服を着たモデルを生成）
        gemini_adapter = self._create_adapter("gemini")
        if not gemini_adapter:
            QMessageBox.warning(self, "エラー", "Gemini APIキーが設定されていません")
            return
        
        # GenerateServiceを作成
        from core.vton.fidelity_check import FidelityChecker
        fidelity_checker = FidelityChecker()
        service = GenerateService(gemini_adapter, fidelity_checker)
        
        # ワーカースレッドで実行（顔交換付き）
        self.worker = ReferencePersonWorker(
            service,
            self.garments,
            model_attrs,
            config,
            self.reference_person_image  # 顔のソース
        )
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.generation_completed.connect(self._on_generation_completed)
        self.worker.generation_failed.connect(self._on_generation_failed)
        
        # UIを更新
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.worker.start()

    def _create_adapter(self, provider: str):
        """プロバイダアダプタを作成"""
        api_key = self.api_key_manager.load_api_key(provider)
        if not api_key:
            return None

        if provider == "openai":
            return OpenAIAdapter(api_key)
        elif provider == "stability":
            return StabilityAdapter(api_key)
        elif provider == "gemini":
            return GeminiImagenAdapter(api_key)
        elif provider == "vertex":
            project_id = self.config_manager.get("GOOGLE_PROJECT_ID")
            return VertexAdapter(api_key, project_id=project_id)

        return None

    def _update_progress(self, percentage: int, message: str):
        """進捗を更新"""
        self.progress_bar.setValue(percentage)
        self.statusBar().showMessage(message)

    def _on_generation_completed(self, images, metadata):
        """生成完了時の処理"""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        self.statusBar().showMessage(f"{len(images)}枚の画像を生成しました", 3000)

        # ギャラリーに表示
        self.gallery_view.set_images(images, metadata)
        
        # 最後の生成パラメータを保存（チャット修正用）
        pose_id, pose_description, _ = self.selected_pose_info
        bg_id, bg_description, _ = self.selected_background_info
        
        self.last_generation_params = {
            "garments": self.garments,
            "model_attrs": {
                "gender": self.gender_combo.currentText(),
                "age_range": self.age_combo.currentText(),
                "ethnicity": self.ethnicity_combo.currentText(),
                "body_type": self.body_type_combo.currentText(),
                "pose": pose_id,
                "background": bg_id,
                "pose_description": pose_description,
                "background_description": bg_description
            },
            "config": {
                "size": self.size_combo.currentText(),
                "num_outputs": self.num_outputs_spin.value()
            }
        }
        
        # 履歴に保存
        self._save_to_history(images, metadata)

    def _on_generation_failed(self, error_message: str):
        """生成失敗時の処理"""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        QMessageBox.critical(self, "エラー", f"画像生成に失敗しました:\n{error_message}")

    def _save_results(self):
        """結果を保存"""
        images = self.gallery_view.get_images()
        if not images:
            QMessageBox.information(self, "情報", "保存する画像がありません。")
            return

        save_dir = QFileDialog.getExistingDirectory(self, "保存先を選択")
        if save_dir:
            try:
                for i, img in enumerate(images):
                    save_path = Path(save_dir) / f"generated_{i+1}.png"
                    img.save(save_path)
                QMessageBox.information(self, "成功", f"{len(images)}枚の画像を保存しました。")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"保存に失敗しました: {e}")

    def _clear_results(self):
        """結果をクリア"""
        self.gallery_view.clear()
    
    def _save_to_history(self, images: List[Image.Image], metadata: Dict):
        """生成結果を履歴に保存"""
        try:
            # 角度情報を抽出
            angles = None
            if metadata.get("mode") == "multi_angle" and metadata.get("angles"):
                angles = [a["angle"] for a in metadata["angles"]]
            
            # パラメータをJSON化可能な形式に変換
            json_safe_params = {}
            for key, value in self.last_generation_params.items():
                if key == "garments":
                    # ClothingItemオブジェクトを辞書に変換
                    json_safe_params[key] = [g.to_dict() for g in value]
                else:
                    json_safe_params[key] = value
            
            # 履歴に保存
            history_id = self.history_manager.save_generation(
                images=images,
                parameters=json_safe_params,
                generation_mode=self.generation_mode,
                angles=angles,
                tags=[],
                notes=""
            )
            
            # 履歴パネルを更新
            self.history_panel.refresh()
            
            print(f"[History] 履歴保存完了: ID={history_id}")
        
        except Exception as e:
            print(f"[History] 履歴保存エラー: {e}")
            # エラーでも処理は続行

    def _setup_menubar(self):
        """メニューバーをセットアップ"""
        menubar = self.menuBar()
        
        # ファイルメニュー
        file_menu = menubar.addMenu("ファイル")
        
        # 設定をエクスポート
        export_action = file_menu.addAction("設定をエクスポート...")
        export_action.triggered.connect(self._export_settings)
        
        # 設定をインポート
        import_action = file_menu.addAction("設定をインポート...")
        import_action.triggered.connect(self._import_settings)
        
        file_menu.addSeparator()
        
        # プロジェクトメニュー
        project_submenu = file_menu.addMenu("プロジェクト")
        
        new_project_action = project_submenu.addAction("新規プロジェクト...")
        new_project_action.triggered.connect(self._new_project)
        
        open_project_action = project_submenu.addAction("プロジェクトを開く...")
        open_project_action.triggered.connect(self._open_project)
        
        project_submenu.addSeparator()
        
        export_project_action = project_submenu.addAction("プロジェクトをエクスポート...")
        export_project_action.triggered.connect(self._export_project)
        
        import_project_action = project_submenu.addAction("プロジェクトをインポート...")
        import_project_action.triggered.connect(self._import_project)
        
        file_menu.addSeparator()
        
        # 終了
        exit_action = file_menu.addAction("終了")
        exit_action.triggered.connect(self.close)
        
        # ツールメニュー
        tools_menu = menubar.addMenu("ツール")
        
        # バッチ処理
        batch_action = tools_menu.addAction("バッチ処理...")
        batch_action.triggered.connect(self._open_batch_processor)
        
        # 色変更ツール
        color_action = tools_menu.addAction("衣類色変更...")
        color_action.triggered.connect(self._open_color_changer)
        
        tools_menu.addSeparator()
        
        # 統計情報
        stats_action = tools_menu.addAction("統計情報")
        stats_action.triggered.connect(self._show_statistics)
        
        # ヘルプメニュー
        help_menu = menubar.addMenu("ヘルプ")
        
        # 使い方
        usage_action = help_menu.addAction("使い方")
        usage_action.triggered.connect(self._show_usage)
        
        # バージョン情報
        about_action = help_menu.addAction("バージョン情報")
        about_action.triggered.connect(self._show_about)
    
    def _export_settings(self):
        """設定をエクスポート"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "設定をエクスポート",
            "",
            "JSON ファイル (*.json)"
        )
        
        if file_path:
            from utils.settings_manager import SettingsManager
            manager = SettingsManager()
            
            # 現在の設定を取得
            if self.last_generation_params:
                success = manager.export_settings(
                    model_attrs=self.last_generation_params["model_attrs"],
                    generation_config=self.last_generation_params["config"],
                    garments_info=[g.to_dict() for g in self.garments],
                    export_path=file_path
                )
                
                if success:
                    QMessageBox.information(self, "成功", "設定をエクスポートしました")
                else:
                    QMessageBox.warning(self, "エラー", "エクスポートに失敗しました")
            else:
                QMessageBox.warning(self, "警告", "エクスポートする設定がありません\n先に画像を生成してください")
    
    def _import_settings(self):
        """設定をインポート"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "設定をインポート",
            "",
            "JSON ファイル (*.json)"
        )
        
        if file_path:
            from utils.settings_manager import SettingsManager
            manager = SettingsManager()
            
            imported = manager.import_settings(file_path)
            
            if imported:
                # UIに設定を反映（TODO: 実装）
                QMessageBox.information(
                    self,
                    "成功",
                    "設定をインポートしました\n※UIへの反映は次回実装します"
                )
            else:
                QMessageBox.warning(self, "エラー", "インポートに失敗しました")
    
    def _new_project(self):
        """新規プロジェクトを作成"""
        from PySide6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self,
            "新規プロジェクト",
            "プロジェクト名:"
        )
        
        if ok and name:
            from core.history.project_manager import ProjectManager
            pm = ProjectManager()
            project = pm.create_project(name)
            
            QMessageBox.information(
                self,
                "成功",
                f"プロジェクト '{name}' を作成しました"
            )
    
    def _open_project(self):
        """プロジェクトを開く"""
        QMessageBox.information(
            self,
            "情報",
            "プロジェクト選択ダイアログ\n※次回実装します"
        )
    
    def _export_project(self):
        """プロジェクトをエクスポート"""
        QMessageBox.information(
            self,
            "情報",
            "プロジェクトエクスポート\n※次回実装します"
        )
    
    def _import_project(self):
        """プロジェクトをインポート"""
        QMessageBox.information(
            self,
            "情報",
            "プロジェクトインポート\n※次回実装します"
        )
    
    def _open_batch_processor(self):
        """バッチ処理ダイアログを開く"""
        QMessageBox.information(
            self,
            "情報",
            "バッチ処理ダイアログ\n※次回実装します"
        )
    
    def _open_color_changer(self):
        """色変更ダイアログを開く"""
        QMessageBox.information(
            self,
            "情報",
            "色変更ツール\n※次回実装します"
        )
    
    def _show_statistics(self):
        """統計情報を表示"""
        try:
            stats = self.history_manager.get_statistics()
            
            stats_text = f"""
生成統計情報

総生成回数: {stats['total_generations']}回
総画像数: {stats['total_images']}枚
お気に入り: {stats['favorite_count']}件

生成モード別:
"""
            for mode, count in stats.get('mode_counts', {}).items():
                mode_name = "角度違い" if mode == "angle" else "種類違い"
                stats_text += f"  - {mode_name}: {count}回\n"
            
            QMessageBox.information(self, "統計情報", stats_text)
        
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"統計情報の取得に失敗: {e}")
    
    def _show_usage(self):
        """使い方を表示"""
        usage_text = """
Virtual Fashion Try-On v2.0 使い方

1. 衣類画像をアップロード
2. モデル属性を選択（基本・ポーズ・背景）
3. 生成モードを選択（種類違い or 角度違い）
4. 生成開始
5. チャットで修正（オプション）

詳細は 使い方ガイド_v2.0.txt をご覧ください。
"""
        QMessageBox.information(self, "使い方", usage_text)
    
    def _show_about(self):
        """バージョン情報を表示"""
        about_text = """
Virtual Fashion Try-On

Version: 2.0
実装日: 2025-11-14

主な機能:
- ポーズ画像ギャラリー
- 背景画像ギャラリー
- マルチアングル生成
- チャット修正機能
- 生成履歴管理
- プロジェクト管理

Powered by:
- Gemini 2.5 Flash Image
- MediaPipe
- PySide6
"""
        QMessageBox.about(self, "バージョン情報", about_text)
    
    def _check_api_keys(self):
        """APIキーの確認（Gemini自動設定機能付き）"""
        # Gemini APIキーが設定されているか確認
        gemini_key = self.api_key_manager.load_api_key("gemini")
        
        if not gemini_key:
            # Gemini APIキーが未設定の場合、自動設定を試みる
            default_api_key = "AIzaSyDLQVe0L5jn6R7lJNV4coe5FY-ICRHtSIg"
            
            reply = QMessageBox.question(
                self,
                "Gemini APIキー自動設定",
                "Gemini APIキーが設定されていません。\n"
                "デフォルトのAPIキーを自動設定しますか？\n\n"
                "※後で設定メニューから変更できます。",
                QMessageBox.Yes | QMessageBox.No,
            )
            
            if reply == QMessageBox.Yes:
                try:
                    self.api_key_manager.save_api_key("gemini", default_api_key)
                    QMessageBox.information(
                        self,
                        "設定完了",
                        "Gemini APIキーが自動設定されました。\n"
                        "すぐに画像生成を開始できます！"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "エラー",
                        f"APIキーの保存に失敗しました:\n{str(e)}"
                    )
            else:
                # 手動設定ダイアログを開く
                self._open_api_key_dialog()
        # APIキーが設定済みの場合は何もしない（情報ダイアログは非表示）

    def _show_info_dialog(self):
        """情報ダイアログを表示"""
        from ui.widgets.info_dialog import InfoDialog
        
        dialog = InfoDialog(self)
        dialog.exec()

    def _open_api_key_dialog(self):
        """APIキー設定ダイアログを開く"""
        from ui.widgets.api_key_dialog import APIKeyDialog

        dialog = APIKeyDialog(self.api_key_manager, self)
        dialog.exec()

