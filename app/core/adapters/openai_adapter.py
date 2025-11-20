"""OpenAI DALL-E 3 adapter"""

import asyncio
import base64
from io import BytesIO
from typing import List, Tuple, Dict, Any
from PIL import Image
import requests
from openai import OpenAI

from models.clothing_item import ClothingItem
from models.model_attributes import ModelAttributes
from models.generation_config import GenerationConfig
from core.adapters.provider_base import ProviderBase


class OpenAIAdapter(ProviderBase):
    """OpenAI DALL-E 3 アダプタ"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = OpenAI(api_key=api_key)
        self.model = "dall-e-3"

    def prepare(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
    ) -> Dict[str, Any]:
        """生成リクエストの準備"""
        from core.pipeline.prompt_generator import PromptGenerator

        generator = PromptGenerator()
        prompts = generator.build_faithful_prompt(garments, model_attrs, config)

        return {
            "model": self.model,
            "prompt": prompts["prompt"],  # 辞書からプロンプト文字列を取得
            "size": config.size,
            "quality": config.quality,
            "n": 1,  # DALL-E 3は常に1
        }

    def generate(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
        num_outputs: int,
    ) -> Tuple[List[Image.Image], Dict[str, Any]]:
        """
        画像生成（DALL-E 3は1枚ずつなので並列/逐次実行）

        Args:
            garments: 衣類アイテムのリスト
            model_attrs: モデル属性
            config: 生成設定
            num_outputs: 出力枚数（1-4）

        Returns:
            (生成画像のリスト, メタデータ)
        """
        images = []
        metadatas = []

        # DALL-E 3はn=1固定なので、num_outputs回リクエストを送る
        for i in range(num_outputs):
            try:
                params = self.prepare(garments, model_attrs, config)

                # APIリクエスト
                response = self.client.images.generate(**params)

                # 画像を取得
                image_url = response.data[0].url
                image = self._download_image(image_url)
                images.append(image)

                # メタデータを保存
                metadatas.append(
                    {
                        "index": i,
                        "model": params["model"],
                        "size": params["size"],
                        "quality": params["quality"],
                        "revised_prompt": response.data[0].revised_prompt,
                    }
                )

            except Exception as e:
                print(f"Error generating image {i+1}/{num_outputs}: {e}")
                # エラーがあっても続行（部分成功を許容）
                continue

        metadata = {
            "provider": "openai",
            "model": self.model,
            "total_images": len(images),
            "requested_images": num_outputs,
            "partials": metadatas,
        }

        return images, metadata

    def _download_image(self, url: str) -> Image.Image:
        """URLから画像をダウンロード"""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))

    def check_api_status(self) -> bool:
        """API接続状態の確認"""
        try:
            # モデルリストを取得して接続確認
            self.client.models.list()
            return True
        except Exception:
            return False

    def estimate_cost(self, config: GenerationConfig) -> float:
        """
        生成コストの見積もり

        DALL-E 3の価格（2024年時点）:
        - 1024×1024: $0.040/image (standard), $0.080/image (hd)
        - 1024×1792, 1792×1024: $0.080/image (standard), $0.120/image (hd)
        """
        if config.size in ["1024x1792", "1792x1024"]:
            cost_per_image = 0.080 if config.quality == "standard" else 0.120
        else:
            cost_per_image = 0.040 if config.quality == "standard" else 0.080

        return cost_per_image * config.num_outputs

    def supports_seed(self) -> bool:
        """DALL-E 3はseedをサポートしない"""
        return False

    def supports_multi_output(self) -> bool:
        """DALL-E 3はn=1固定のため、複数出力をネイティブサポートしない"""
        return False

