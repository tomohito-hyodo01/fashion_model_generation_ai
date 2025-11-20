"""Multi-angle image generation"""

import copy
import sys
from typing import List, Tuple, Dict, Any
from PIL import Image
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.models.clothing_item import ClothingItem
from app.models.model_attributes import ModelAttributes
from app.models.generation_config import GenerationConfig


class MultiAngleGenerator:
    """複数角度からの画像生成
    
    同じ衣類・モデルで異なる角度から画像を生成します
    """
    
    # 角度ごとのポーズ記述
    ANGLE_DESCRIPTIONS = {
        0: {
            "name": "正面",
            "pose": "front",
            "description": "standing straight, facing directly at camera, front view, full body visible from head to feet"
        },
        45: {
            "name": "斜め前",
            "pose": "three_quarter_front",
            "description": "standing at three-quarter front view, 45 degrees angle, slightly turned, full body visible"
        },
        90: {
            "name": "側面",
            "pose": "side",
            "description": "standing in profile view, side pose, 90 degrees angle, full body visible from head to feet"
        },
        135: {
            "name": "斜め後ろ",
            "pose": "three_quarter_back",
            "description": "standing at three-quarter back view, 135 degrees angle, slightly turned away, full body visible"
        },
        180: {
            "name": "背面",
            "pose": "back",
            "description": "standing facing away from camera, back view, 180 degrees angle, full body visible from head to feet"
        },
        -45: {
            "name": "斜め前（左）",
            "pose": "three_quarter_front_left",
            "description": "standing at three-quarter front view from left, 45 degrees angle, slightly turned to the left, full body visible"
        },
        -90: {
            "name": "側面（左）",
            "pose": "side_left",
            "description": "standing in profile view from left side, 90 degrees angle, full body visible from head to feet"
        }
    }
    
    # プリセット角度セット
    PRESET_ANGLES = {
        "2angles": [0, 180],  # 前後
        "3angles": [0, 90, 180],  # 前・横・後
        "4angles": [0, 45, 90, 135],  # 前・斜め前・横・斜め後ろ
        "full": [0, 45, 90, 135, 180, -45, -90]  # 全方向
    }
    
    def __init__(self):
        """初期化"""
        pass
    
    def get_angle_configurations(self, num_outputs: int) -> List[int]:
        """出力枚数に応じた角度設定を取得
        
        Args:
            num_outputs: 出力枚数（1-4）
        
        Returns:
            角度のリスト
        """
        if num_outputs == 1:
            return [0]  # 正面のみ
        elif num_outputs == 2:
            return self.PRESET_ANGLES["2angles"]
        elif num_outputs == 3:
            return self.PRESET_ANGLES["3angles"]
        elif num_outputs >= 4:
            return self.PRESET_ANGLES["4angles"]
        else:
            return [0]
    
    def create_angle_model_attributes(
        self,
        base_model_attrs: ModelAttributes,
        angle: int
    ) -> ModelAttributes:
        """指定された角度用のModelAttributesを作成
        
        Args:
            base_model_attrs: ベースとなるモデル属性
            angle: 角度（度）
        
        Returns:
            角度が反映されたModelAttributes
        """
        # ベース属性をコピー
        angle_attrs = copy.deepcopy(base_model_attrs)
        
        # 角度に応じた設定を取得
        angle_config = self.ANGLE_DESCRIPTIONS.get(angle, self.ANGLE_DESCRIPTIONS[0])
        
        # ポーズと説明を更新
        angle_attrs.pose = angle_config["pose"]
        
        # カスタム説明を更新（既存の説明を保持しつつ角度情報を追加）
        base_description = angle_attrs.custom_description or ""
        angle_description = angle_config["description"]
        
        # 角度情報を追加
        if base_description:
            # 既存の説明からポーズ部分を除去（重複を避ける）
            if "Pose:" in base_description:
                parts = base_description.split("Pose:")
                other_parts = parts[0]
                if "Background:" in base_description:
                    bg_part = "Background:" + base_description.split("Background:")[1]
                    angle_attrs.custom_description = f"{other_parts}Pose: {angle_description}. {bg_part}".strip()
                else:
                    angle_attrs.custom_description = f"{other_parts}Pose: {angle_description}".strip()
            else:
                angle_attrs.custom_description = f"{base_description}. Pose: {angle_description}".strip()
        else:
            angle_attrs.custom_description = f"Pose: {angle_description}"
        
        return angle_attrs
    
    async def generate_multi_angle(
        self,
        generate_service,
        garments: List[ClothingItem],
        base_model_attrs: ModelAttributes,
        base_config: GenerationConfig,
        angles: List[int],
        progress_callback=None
    ) -> Tuple[List[Image.Image], Dict[str, Any]]:
        """複数角度から画像を生成
        
        Args:
            generate_service: GenerateServiceインスタンス
            garments: 衣類アイテムのリスト
            base_model_attrs: ベースとなるモデル属性
            base_config: ベースとなる生成設定
            angles: 生成する角度のリスト
            progress_callback: 進捗コールバック関数
        
        Returns:
            (生成画像のリスト, メタデータ)
        """
        all_images = []
        all_metadata = []
        
        # 一貫性のためにseedを固定
        if base_config.seed is None:
            import random
            base_config.seed = random.randint(0, 1000000)
        
        print(f"\n[Multi-Angle] {len(angles)}つの角度から生成します")
        print(f"[Multi-Angle] 使用するseed: {base_config.seed}")
        
        # 各角度で生成
        for i, angle in enumerate(angles):
            angle_name = self.ANGLE_DESCRIPTIONS.get(angle, {}).get("name", f"{angle}度")
            print(f"\n[Multi-Angle] 角度 {i+1}/{len(angles)}: {angle_name} ({angle}度)")
            
            # 進捗報告
            if progress_callback:
                progress = 10 + int((i / len(angles)) * 80)
                progress_callback(f"角度 {i+1}/{len(angles)}: {angle_name} を生成中...", progress)
            
            # 角度用のモデル属性を作成
            angle_attrs = self.create_angle_model_attributes(base_model_attrs, angle)
            
            # 設定をコピー（1枚ずつ生成）
            angle_config = copy.deepcopy(base_config)
            angle_config.num_outputs = 1
            
            try:
                # 生成実行
                images, metadata = await generate_service.run(
                    garments,
                    angle_attrs,
                    angle_config
                )
                
                if images:
                    all_images.extend(images)
                    all_metadata.append({
                        "angle": angle,
                        "angle_name": angle_name,
                        "metadata": metadata
                    })
                    print(f"[Multi-Angle] ✓ {angle_name} の生成完了")
                else:
                    print(f"[Multi-Angle] ✗ {angle_name} の生成失敗")
            
            except Exception as e:
                print(f"[Multi-Angle] ✗ {angle_name} でエラー: {e}")
                continue
        
        # 最終メタデータ
        final_metadata = {
            "mode": "multi_angle",
            "total_angles": len(angles),
            "generated_images": len(all_images),
            "seed": base_config.seed,
            "angles": all_metadata
        }
        
        return all_images, final_metadata
    
    def get_angle_name(self, angle: int) -> str:
        """角度名を取得"""
        return self.ANGLE_DESCRIPTIONS.get(angle, {}).get("name", f"{angle}度")


# 使用例
if __name__ == "__main__":
    generator = MultiAngleGenerator()
    
    # 各枚数での角度設定を表示
    for num in range(1, 5):
        angles = generator.get_angle_configurations(num)
        print(f"\n{num}枚生成時の角度:")
        for angle in angles:
            print(f"  - {angle}度: {generator.get_angle_name(angle)}")

