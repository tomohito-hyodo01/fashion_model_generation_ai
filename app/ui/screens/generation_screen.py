"""Generation screen - New image generation page"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QRadioButton,
    QPushButton,
    QButtonGroup,
    QScrollArea,
    QTabWidget,
    QProgressBar,
    QFileDialog,
    QMessageBox,
    QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PIL import Image
from typing import List, Dict, Optional
from pathlib import Path

from ui.styles import Styles, Colors, Fonts, Spacing, BorderRadius
from ui.widgets.garment_slot import GarmentSlotWidget
from ui.widgets.reference_person_widget import ReferencePersonWidget
from ui.widgets.pose_gallery import PoseGalleryWidget
from ui.widgets.background_gallery import BackgroundGalleryWidget
from models.clothing_item import ClothingItem


class GenerationScreen(QWidget):
    """新規生成画面"""

    # シグナル
    generation_requested = Signal(dict)  # 生成パラメータ
    reference_person_changed = Signal(str)  # 参考人物画像パス (空文字列でクリア)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.garments: List[ClothingItem] = []
        self.garment_slots: List[GarmentSlotWidget] = []
        self.selected_pose_info = ("front", "正面を向いて立つ")
        self.selected_background_info = ("white", "白背景")
        self._setup_ui()

    def _setup_ui(self):
        """UIをセットアップ"""
        # メインスクロールエリア
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(Styles.SCROLL_AREA)

        # スクロールコンテンツ
        scroll_content = QWidget()
        scroll_content.setStyleSheet(f"background-color: {Colors.BG_MAIN};")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        content_layout.setSpacing(Spacing.LG)

        # ===== 参考人物セクション =====
        person_group = self._create_reference_person_group()
        content_layout.addWidget(person_group)

        # ===== 衣類画像セクション =====
        garment_group = self._create_garment_group()
        content_layout.addWidget(garment_group)

        # ===== モデル属性セクション =====
        attrs_group = self._create_model_attributes_group()
        content_layout.addWidget(attrs_group)

        # ===== 生成設定セクション =====
        settings_group = self._create_generation_settings_group()
        content_layout.addWidget(settings_group)

        # スペーサー
        content_layout.addStretch()

        scroll.setWidget(scroll_content)

        # メインレイアウト
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _create_reference_person_group(self) -> QGroupBox:
        """参考人物グループを作成"""
        group = QGroupBox("参考人物")
        group.setStyleSheet(Styles.GROUP_BOX)
        layout = QVBoxLayout()
        layout.setContentsMargins(Spacing.MD, Spacing.LG, Spacing.MD, Spacing.MD)

        # 説明ラベル
        desc = QLabel("参考人物の画像を設定すると、その人物に衣類を着せた画像が生成されます（オプション）")
        desc.setWordWrap(True)
        desc.setStyleSheet(Styles.LABEL_MUTED)
        layout.addWidget(desc)

        # 参考人物ウィジェット
        self.reference_person_widget = ReferencePersonWidget()
        self.reference_person_widget.person_set.connect(self._on_reference_person_set)
        self.reference_person_widget.person_cleared.connect(self._on_reference_person_cleared)
        layout.addWidget(self.reference_person_widget)

        group.setLayout(layout)
        return group

    def _create_garment_group(self) -> QGroupBox:
        """衣類画像グループを作成"""
        group = QGroupBox("衣類画像")
        group.setStyleSheet(Styles.GROUP_BOX)
        layout = QVBoxLayout()
        layout.setContentsMargins(Spacing.MD, Spacing.LG, Spacing.MD, Spacing.MD)

        # 説明ラベル
        desc = QLabel("着せたい衣類の画像をアップロードしてください（複数可）")
        desc.setWordWrap(True)
        desc.setStyleSheet(Styles.LABEL_MUTED)
        layout.addWidget(desc)

        # 衣類スロットコンテナ
        self.garment_container = QWidget()
        self.garment_container.setStyleSheet("background: transparent;")
        self.garment_layout = QHBoxLayout(self.garment_container)
        self.garment_layout.setContentsMargins(0, 0, 0, 0)
        self.garment_layout.setSpacing(Spacing.MD)
        self.garment_layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.garment_container)

        # 追加ボタン（青ボタン白文字）
        add_btn = QPushButton("+ 衣類画像を追加")
        add_btn.setMinimumHeight(44)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_garment_image)
        layout.addWidget(add_btn, alignment=Qt.AlignLeft)

        group.setLayout(layout)
        return group

    def _create_model_attributes_group(self) -> QGroupBox:
        """モデル属性グループを作成"""
        self.model_attrs_group = QGroupBox("モデル属性")
        self.model_attrs_group.setStyleSheet(Styles.GROUP_BOX)
        layout = QVBoxLayout()
        layout.setContentsMargins(Spacing.MD, Spacing.LG, Spacing.MD, Spacing.MD)

        # タブウィジェット
        self.model_attrs_tab_widget = QTabWidget()
        self.model_attrs_tab_widget.setStyleSheet(Styles.TAB_WIDGET)

        # 基本タブ
        basic_tab = self._create_basic_attributes_tab()
        self.model_attrs_tab_widget.addTab(basic_tab, "基本")

        # ポーズタブ
        pose_tab = self._create_pose_tab()
        self.model_attrs_tab_widget.addTab(pose_tab, "ポーズ")

        # 背景タブ
        bg_tab = self._create_background_tab()
        self.model_attrs_tab_widget.addTab(bg_tab, "背景")

        layout.addWidget(self.model_attrs_tab_widget)
        self.model_attrs_group.setLayout(layout)
        return self.model_attrs_group

    def _create_basic_attributes_tab(self) -> QWidget:
        """基本属性タブを作成"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.LG)

        # 性別 (表示用とデータ用のマッピング)
        self._gender_map = {"女性": "female", "男性": "male"}
        gender_layout = QVBoxLayout()
        gender_label = QLabel("性別")
        gender_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        gender_layout.addWidget(gender_label)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(list(self._gender_map.keys()))
        self.gender_combo.setStyleSheet(Styles.COMBO_BOX)
        self.gender_combo.setMinimumHeight(36)
        gender_layout.addWidget(self.gender_combo)
        layout.addLayout(gender_layout)

        # 年代
        self._age_map = {"10代": "10s", "20代": "20s", "30代": "30s", "40代": "40s", "50代以上": "50s+"}
        age_layout = QVBoxLayout()
        age_label = QLabel("年代")
        age_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        age_layout.addWidget(age_label)
        self.age_combo = QComboBox()
        self.age_combo.addItems(list(self._age_map.keys()))
        self.age_combo.setCurrentIndex(1)
        self.age_combo.setStyleSheet(Styles.COMBO_BOX)
        self.age_combo.setMinimumHeight(36)
        age_layout.addWidget(self.age_combo)
        layout.addLayout(age_layout)

        # 地域/民族
        self._ethnicity_map = {
            "アジア系": "asian",
            "ヨーロッパ系": "european",
            "アフリカ系": "african",
            "ラテン系": "latin",
            "中東系": "middle_eastern",
            "ミックス": "mixed"
        }
        ethnicity_layout = QVBoxLayout()
        ethnicity_label = QLabel("地域/民族")
        ethnicity_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        ethnicity_layout.addWidget(ethnicity_label)
        self.ethnicity_combo = QComboBox()
        self.ethnicity_combo.addItems(list(self._ethnicity_map.keys()))
        self.ethnicity_combo.setStyleSheet(Styles.COMBO_BOX)
        self.ethnicity_combo.setMinimumHeight(36)
        ethnicity_layout.addWidget(self.ethnicity_combo)
        layout.addLayout(ethnicity_layout)

        # 体型
        self._body_type_map = {"スリム": "slim", "標準": "standard", "アスレチック": "athletic", "プラスサイズ": "plus-size"}
        body_layout = QVBoxLayout()
        body_label = QLabel("体型")
        body_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        body_layout.addWidget(body_label)
        self.body_type_combo = QComboBox()
        self.body_type_combo.addItems(list(self._body_type_map.keys()))
        self.body_type_combo.setCurrentIndex(1)
        self.body_type_combo.setStyleSheet(Styles.COMBO_BOX)
        self.body_type_combo.setMinimumHeight(36)
        body_layout.addWidget(self.body_type_combo)
        layout.addLayout(body_layout)

        layout.addStretch()
        return tab

    def _create_pose_tab(self) -> QWidget:
        """ポーズタブを作成"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)

        self.pose_gallery = PoseGalleryWidget()
        self.pose_gallery.pose_selected.connect(self._on_pose_selected)
        layout.addWidget(self.pose_gallery)

        return tab

    def _create_background_tab(self) -> QWidget:
        """背景タブを作成"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)

        self.background_gallery = BackgroundGalleryWidget()
        self.background_gallery.background_selected.connect(self._on_background_selected)
        layout.addWidget(self.background_gallery)

        return tab

    def _create_generation_settings_group(self) -> QGroupBox:
        """生成設定グループを作成"""
        group = QGroupBox("生成設定")
        group.setStyleSheet(Styles.GROUP_BOX)
        layout = QVBoxLayout()
        layout.setContentsMargins(Spacing.MD, Spacing.LG, Spacing.MD, Spacing.MD)

        # 設定行
        settings_row = QHBoxLayout()
        settings_row.setSpacing(Spacing.LG)

        # 画像サイズ
        size_layout = QVBoxLayout()
        size_label = QLabel("画像サイズ")
        size_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        size_layout.addWidget(size_label)
        self.size_combo = QComboBox()
        self.size_combo.addItems(["1024x1024", "1024x1792", "1792x1024"])
        self.size_combo.setStyleSheet(Styles.COMBO_BOX)
        self.size_combo.setMinimumHeight(40)
        self.size_combo.setMinimumWidth(140)
        size_layout.addWidget(self.size_combo)
        settings_row.addLayout(size_layout)

        # 出力枚数
        num_layout = QVBoxLayout()
        num_label = QLabel("出力枚数")
        num_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        num_layout.addWidget(num_label)
        self.num_outputs_spin = QSpinBox()
        self.num_outputs_spin.setRange(1, 4)
        self.num_outputs_spin.setValue(1)  # デフォルト1枚
        self.num_outputs_spin.setStyleSheet(Styles.SPIN_BOX)
        self.num_outputs_spin.setMinimumHeight(40)
        self.num_outputs_spin.setMinimumWidth(100)
        self.num_outputs_spin.valueChanged.connect(self._on_num_outputs_changed)
        num_layout.addWidget(self.num_outputs_spin)
        settings_row.addLayout(num_layout)

        # 動画生成
        video_layout = QVBoxLayout()
        video_label = QLabel("動画生成")
        video_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        video_layout.addWidget(video_label)
        self.video_checkbox = QCheckBox("動画も生成する")
        self.video_checkbox.setStyleSheet(Styles.CHECK_BOX)
        self.video_checkbox.setMinimumHeight(40)
        self.video_checkbox.setEnabled(False)  # 初期状態は無効（枚数1のため）
        self.video_checkbox.stateChanged.connect(self._on_video_checkbox_changed)
        video_layout.addWidget(self.video_checkbox)
        settings_row.addLayout(video_layout)

        # 動画秒数
        duration_layout = QVBoxLayout()
        duration_label = QLabel("動画秒数")
        duration_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        duration_layout.addWidget(duration_label)
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["5秒", "10秒"])
        self.duration_combo.setStyleSheet(Styles.COMBO_BOX)
        self.duration_combo.setMinimumHeight(40)
        self.duration_combo.setMinimumWidth(80)
        self.duration_combo.setEnabled(False)  # 初期状態は無効
        duration_layout.addWidget(self.duration_combo)
        settings_row.addLayout(duration_layout)

        settings_row.addStretch()
        layout.addLayout(settings_row)

        layout.addSpacing(Spacing.MD)

        # 生成モード
        mode_layout = QHBoxLayout()
        mode_label = QLabel("生成モード:")
        mode_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        mode_layout.addWidget(mode_label)

        self.mode_group = QButtonGroup(self)
        self.mode_variation = QRadioButton("種類違い")
        self.mode_variation.setChecked(True)
        self.mode_variation.setStyleSheet(Styles.RADIO_BUTTON)
        self.mode_group.addButton(self.mode_variation)
        mode_layout.addWidget(self.mode_variation)

        self.mode_angle = QRadioButton("角度違い")
        self.mode_angle.setStyleSheet(Styles.RADIO_BUTTON)
        self.mode_group.addButton(self.mode_angle)
        mode_layout.addWidget(self.mode_angle)

        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        layout.addSpacing(Spacing.MD)

        # 生成ボタン/プログレスバー切り替え用のスタックウィジェット
        from PySide6.QtWidgets import QStackedWidget
        self.generate_stack = QStackedWidget()
        self.generate_stack.setMinimumHeight(52)

        # 生成開始ボタン (index 0)
        self.generate_btn = QPushButton("生成開始")
        self.generate_btn.setMinimumHeight(52)
        self.generate_btn.setCursor(Qt.PointingHandCursor)
        self.generate_btn.setStyleSheet(Styles.BUTTON_SUCCESS)
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        self.generate_stack.addWidget(self.generate_btn)

        # プログレスバー (index 1)
        self.inline_progress_bar = QProgressBar()
        self.inline_progress_bar.setMinimum(0)
        self.inline_progress_bar.setMaximum(100)
        self.inline_progress_bar.setMinimumHeight(52)
        self.inline_progress_bar.setTextVisible(True)
        self.inline_progress_bar.setFormat("生成中... %p%")
        self.inline_progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {Colors.BG_TERTIARY};
                border: none;
                border-radius: 8px;
                text-align: center;
                font-weight: 600;
                font-size: 14px;
                color: {Colors.TEXT_PRIMARY};
            }}
            QProgressBar::chunk {{
                background-color: {Colors.PRIMARY};
                border-radius: 8px;
            }}
        """)
        self.generate_stack.addWidget(self.inline_progress_bar)

        layout.addWidget(self.generate_stack)

        group.setLayout(layout)
        return group

    # ===== イベントハンドラ =====

    def _on_reference_person_set(self, image_path: str, person_name: str):
        """参考人物が設定された時"""
        self.reference_person_changed.emit(image_path)
        # モデル属性を非活性化（参考人物使用時は不要）
        self._set_model_attrs_enabled(False)

    def _on_reference_person_cleared(self):
        """参考人物がクリアされた時"""
        self.reference_person_changed.emit("")
        # モデル属性を活性化
        self._set_model_attrs_enabled(True)

    def _set_model_attrs_enabled(self, enabled: bool):
        """モデル属性の活性/非活性を切り替え（グレーアウト効果付き）"""
        self.model_attrs_tab_widget.setEnabled(enabled)

        # グループボックスのタイトルとスタイルを変更
        if enabled:
            self.model_attrs_group.setTitle("モデル属性")
            # 通常のスタイルに戻す
            self.model_attrs_group.setStyleSheet(Styles.GROUP_BOX)
        else:
            self.model_attrs_group.setTitle("モデル属性（参考人物使用時は無効）")
            # グレーアウト効果を適用
            self.model_attrs_group.setStyleSheet(f"""
                QGroupBox {{
                    font-weight: 500;
                    font-size: {Fonts.SIZE_SM};
                    color: {Colors.TEXT_MUTED};
                    background-color: {Colors.BG_TERTIARY};
                    border: 1px solid {Colors.BORDER_LIGHT};
                    border-top: 2px solid {Colors.BORDER_MEDIUM};
                    border-radius: {BorderRadius.MD}px;
                    margin-top: 8px;
                    padding: 16px;
                    padding-top: 28px;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    left: 12px;
                    top: 8px;
                    padding: 2px 8px;
                    background-color: {Colors.BG_TERTIARY};
                    color: {Colors.TEXT_MUTED};
                    font-weight: 600;
                    font-size: {Fonts.SIZE_SM};
                }}
                QLabel {{
                    color: {Colors.TEXT_MUTED};
                }}
                QComboBox {{
                    background-color: {Colors.BG_TERTIARY};
                    color: {Colors.TEXT_MUTED};
                    border-color: {Colors.BORDER_LIGHT};
                }}
                QTabWidget::pane {{
                    background-color: {Colors.BG_TERTIARY};
                }}
                QTabBar::tab {{
                    background-color: {Colors.BG_TERTIARY};
                    color: {Colors.TEXT_MUTED};
                }}
                QTabBar::tab:selected {{
                    background-color: {Colors.BG_TERTIARY};
                    color: {Colors.TEXT_MUTED};
                }}
            """)

    def _add_garment_image(self):
        """衣類画像を追加"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "衣類画像を選択",
            "",
            "画像ファイル (*.png *.jpg *.jpeg *.webp)"
        )

        if file_path:
            try:
                # 衣類タイプと表裏を選択
                result = self._select_clothing_type_and_side()
                if not result:
                    return
                clothing_type, side = result

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
                item = ClothingItem(
                    image_path=file_path,
                    clothing_type=clothing_type,
                    colors=features.get("colors", []),
                    analyzed_description=description,
                    side=side,
                )
                self.garments.append(item)

                # スロットを追加
                slot = GarmentSlotWidget(item)
                slot.remove_requested.connect(lambda i=item: self._remove_garment(i))
                self.garment_layout.addWidget(slot)
                self.garment_slots.append(slot)

            except Exception as e:
                QMessageBox.critical(self, "エラー", f"画像の読み込みに失敗しました:\n{e}")

    def _select_clothing_type_and_side(self) -> Optional[tuple]:
        """衣類タイプと表裏を選択"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("衣類情報を選択")
        dialog.setMinimumWidth(300)

        # ダイアログ全体のスタイル（黒文字）
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.BG_CARD};
            }}
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Fonts.SIZE_MD};
            }}
            QComboBox {{
                color: {Colors.TEXT_PRIMARY};
                background-color: {Colors.BG_INPUT};
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: {BorderRadius.SM}px;
                padding: 8px 12px;
                min-height: 20px;
            }}
            QComboBox:hover {{
                border-color: {Colors.PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox QAbstractItemView {{
                color: {Colors.TEXT_PRIMARY};
                background-color: {Colors.BG_CARD};
                selection-background-color: {Colors.PRIMARY};
                selection-color: {Colors.TEXT_WHITE};
                border: 1px solid {Colors.BORDER_LIGHT};
            }}
        """)

        layout = QVBoxLayout(dialog)

        # 衣類タイプ選択
        type_layout = QHBoxLayout()
        type_label = QLabel("タイプ:")
        type_combo = QComboBox()
        type_combo.addItems(["トップス", "ボトムス", "アウター", "ワンピース", "アクセサリー"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(type_combo)
        layout.addLayout(type_layout)

        # 表裏選択
        side_layout = QHBoxLayout()
        side_label = QLabel("表裏:")
        side_combo = QComboBox()
        side_combo.addItems(["表", "裏"])
        side_layout.addWidget(side_label)
        side_layout.addWidget(side_combo)
        layout.addLayout(side_layout)

        # ボタン
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() != QDialog.Accepted:
            return None

        # 日本語 → 英語に変換
        type_map = {
            "トップス": "TOP",
            "ボトムス": "BOTTOM",
            "アウター": "OUTER",
            "ワンピース": "ONE_PIECE",
            "アクセサリー": "ACCESSORY"
        }
        side_map = {
            "表": "front",
            "裏": "back"
        }

        clothing_type = type_map.get(type_combo.currentText(), "TOP")
        side = side_map.get(side_combo.currentText(), "front")

        return (clothing_type, side)

    def _remove_garment(self, item: ClothingItem):
        """衣類を削除"""
        if item in self.garments:
            idx = self.garments.index(item)
            self.garments.remove(item)

            # スロットを削除
            if idx < len(self.garment_slots):
                slot = self.garment_slots.pop(idx)
                self.garment_layout.removeWidget(slot)
                slot.deleteLater()

    def _on_video_checkbox_changed(self, state):
        """動画生成チェックボックスの状態が変わった時"""
        # PySide6ではstateChangedはQt.CheckState enumまたはintを渡す
        # Qt.CheckState.Checked == 2
        is_checked = state == Qt.CheckState.Checked or state == 2
        self.duration_combo.setEnabled(is_checked)

    def _on_num_outputs_changed(self, value: int):
        """出力枚数が変わった時"""
        # 出力枚数が2以上の場合のみ動画生成を有効にする
        can_generate_video = value >= 2
        self.video_checkbox.setEnabled(can_generate_video)
        if not can_generate_video:
            self.video_checkbox.setChecked(False)
            self.duration_combo.setEnabled(False)

    def _on_back_image_added(self, item: ClothingItem, file_path: str):
        """裏面画像が追加された時"""
        try:
            # 裏面画像を分析
            from core.vton.clothing_analyzer import ClothingAnalyzer
            analyzer = ClothingAnalyzer()

            try:
                features = analyzer.analyze_clothing(file_path)
                description = analyzer.generate_detailed_description(features, item.clothing_type)
                item.back_analyzed_description = description
                print(f"[Back Image] 裏面画像を分析しました: {description[:50]}...")
            except Exception as analysis_error:
                print(f"Warning: Failed to analyze back image: {analysis_error}")
                item.back_analyzed_description = f"back view of {item.clothing_type.lower()} garment"

        except Exception as e:
            print(f"Error analyzing back image: {e}")

    def _on_pose_selected(self, pose_id: str, pose_description: str):
        """ポーズが選択された時"""
        self.selected_pose_info = (pose_id, pose_description)

    def _on_background_selected(self, bg_id: str, bg_description: str):
        """背景が選択された時"""
        self.selected_background_info = (bg_id, bg_description)

    def _on_generate_clicked(self):
        """生成ボタンがクリックされた時"""
        if not self.garments:
            QMessageBox.warning(
                self,
                "警告",
                "衣類画像を1つ以上追加してください\n\n"
                "「+ 衣類画像を追加」ボタンをクリックして\n"
                "画像をアップロードしてください。"
            )
            return

        # 日本語表示からデータ値に変換
        gender_text = self.gender_combo.currentText()
        age_text = self.age_combo.currentText()
        ethnicity_text = self.ethnicity_combo.currentText()
        body_type_text = self.body_type_combo.currentText()

        # 動画秒数を取得（"5秒" -> 5）
        duration_text = self.duration_combo.currentText()
        video_duration = int(duration_text.replace("秒", ""))

        # パラメータを収集
        params = {
            "garments": self.garments,
            "model_attrs": {
                "gender": self._gender_map.get(gender_text, "female"),
                "age_range": self._age_map.get(age_text, "20s"),
                "ethnicity": self._ethnicity_map.get(ethnicity_text, "asian"),
                "body_type": self._body_type_map.get(body_type_text, "standard"),
                "pose": self.selected_pose_info[0],
                "background": self.selected_background_info[0],
                "pose_description": self.selected_pose_info[1],
                "background_description": self.selected_background_info[1],
            },
            "config": {
                "size": self.size_combo.currentText(),
                "num_outputs": self.num_outputs_spin.value(),
            },
            "generate_video": self.video_checkbox.isChecked(),
            "video_duration": video_duration,
            "generation_mode": "angle" if self.mode_angle.isChecked() else "variation",
        }

        # シグナルを発火
        self.generation_requested.emit(params)

    # ===== 公開メソッド =====

    def set_progress(self, message: str, value: int):
        """進捗を設定（インラインプログレスバー使用）"""
        self.inline_progress_bar.setValue(value)
        self.inline_progress_bar.setFormat(f"{message} %p%")

    def hide_progress(self):
        """進捗を非表示（ボタンに戻す）"""
        self.generate_stack.setCurrentIndex(0)  # ボタンを表示
        self.inline_progress_bar.setValue(0)

    def set_generating(self, is_generating: bool):
        """生成中状態を設定"""
        if is_generating:
            # プログレスバーに切り替え
            self.generate_stack.setCurrentIndex(1)
            self.inline_progress_bar.setValue(0)
        else:
            # ボタンに戻す
            self.generate_stack.setCurrentIndex(0)

    def get_reference_person_path(self) -> Optional[str]:
        """参考人物画像のパスを取得"""
        return self.reference_person_widget.get_person_image_path()

    def update_styles(self):
        """テーマ変更時にスタイルを更新"""
        # 必要に応じてスタイルを更新
        pass
