"""Prompt generation for faithful clothing reproduction"""

from typing import List, Dict
from models.clothing_item import ClothingItem
from models.model_attributes import ModelAttributes
from models.generation_config import GenerationConfig


class PromptGenerator:
    """プロンプト生成エンジン"""

    def build_faithful_prompt(
        self,
        clothing_items: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
    ) -> Dict[str, str]:
        """
        衣類を忠実に再現するプロンプトを構築

        Args:
            clothing_items: 衣類アイテムのリスト
            model_attrs: モデル属性
            config: 生成設定

        Returns:
            {"prompt": str, "negative_prompt": str}
        """
        # 人物を最優先に記述（image-to-imageで極めて重要）
        # 1. モデル描写（最優先）
        model_desc = model_attrs.to_description()

        # 2. 撮影スタイル
        photo_style = self._generate_photography_style(config)
        
        # 3. 衣類の詳細描写
        clothing_desc = self._generate_clothing_description(clothing_items)

        # 最終プロンプト構築（明確に人物を生成するよう指示）
        prompt = (
            f"GENERATE A PHOTOGRAPH OF: {model_desc}. "
            f"COMPOSITION: {photo_style}. "
            f"OUTFIT: {clothing_desc}. "
            f"IMPORTANT: This must show a REAL HUMAN PERSON wearing clothing, NOT just the clothing item alone."
        )

        # ネガティブプロンプト
        negative_prompt = self._generate_negative_prompt()

        return {"prompt": prompt, "negative_prompt": negative_prompt}

    def _generate_constraint(self) -> str:
        """強制制約の生成"""
        return ""  # image-to-imageモードでは、プロンプトは簡潔に

    def _generate_clothing_description(self, items: List[ClothingItem]) -> str:
        """衣類の詳細描写の生成（image-to-image用に最適化）"""
        if not items:
            return "A professional fashion model in a full body photo"

        # 衣類タイプを取得
        clothing_type_desc = []
        for item in items:
            type_map = {
                "TOP": "a top/shirt",
                "BOTTOM": "pants/trousers",
                "OUTER": "a jacket/outerwear",
                "ONE_PIECE": "a dress/outfit",
                "ACCESSORY": "accessories"
            }
            clothing_type_desc.append(type_map.get(item.clothing_type, "clothing"))
        
        # プロンプト構築：人物を最優先に記述
        desc = f"A professional fashion model wearing {' and '.join(clothing_type_desc)} with colors and patterns from the reference image"
        
        return desc

    def _generate_photography_style(self, config: GenerationConfig) -> str:
        """撮影スタイルの生成"""
        return "full body portrait showing entire person from head to feet, professional studio photograph, even lighting, plain white background"

    def _generate_negative_prompt(self) -> str:
        """ネガティブプロンプトの生成（Stability AI用）"""
        return (
            "no person, no human, no model, only clothing, clothing only, garment only, "
            "flat lay, product photo, clothing without person, empty clothing, "
            "hanger, mannequin without body, invisible person, "
            "cropped body, partial body, upper body only, portrait, headshot, close-up, "
            "cut off feet, cut off head, cut off legs, "
            "painting, illustration, drawing, anime, cartoon, 3D render, "
            "blur, low quality, distorted, deformed, bad anatomy"
        )

