"""Stability AI SD 3.5 adapter with image-to-image support"""

import base64
from io import BytesIO
from typing import List, Tuple, Dict, Any
from PIL import Image
import requests

from models.clothing_item import ClothingItem
from models.model_attributes import ModelAttributes
from models.generation_config import GenerationConfig
from core.adapters.provider_base import ProviderBase


class StabilityAdapter(ProviderBase):
    """Stability AI SD 3.5 アダプタ（image-to-image対応）"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.api_host = "https://api.stability.ai"
        self.engine_id = "sd3.5-large"  # SD 3.5に更新
        self.use_image_to_image = True  # image-to-image機能を使用

    def prepare(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
    ) -> Dict[str, Any]:
        """生成リクエストの準備（SD 3.5用）"""
        from core.pipeline.prompt_generator import PromptGenerator

        generator = PromptGenerator()
        prompts = generator.build_faithful_prompt(garments, model_attrs, config)

        # SD 3.5のパラメータ
        return {
            "prompt": prompts["prompt"],
            "negative_prompt": prompts["negative_prompt"],
            "mode": "image-to-image" if garments else "text-to-image",
            "cfg_scale": min(config.cfg_scale, 10.0),  # SD 3.5の上限は10
            "seed": config.seed if config.seed else 0,
            "output_format": "png",
        }

    def generate(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
        num_outputs: int,
    ) -> Tuple[List[Image.Image], Dict[str, Any]]:
        """
        画像生成（SD 3.5 image-to-image使用）

        Args:
            garments: 衣類アイテムのリスト
            model_attrs: モデル属性
            config: 生成設定
            num_outputs: 出力枚数（1-4）

        Returns:
            (生成画像のリスト, メタデータ)
        """
        images = []
        
        # 各出力画像ごとに生成（SD 3.5は1枚ずつ）
        for i in range(num_outputs):
            try:
                if garments and self.use_image_to_image:
                    # image-to-image モード（衣類画像を参照）
                    img, meta = self._generate_image_to_image(
                        garments, model_attrs, config
                    )
                else:
                    # text-to-image モード（フォールバック）
                    img, meta = self._generate_text_to_image(
                        garments, model_attrs, config
                    )
                
                if img:
                    images.append(img)
                    print(f"[Stability AI] Successfully generated image {i+1}/{num_outputs}")
                    
            except Exception as e:
                print(f"Error generating image {i+1}/{num_outputs}: {e}")
                continue

        metadata = {
            "provider": "stability",
            "engine_id": self.engine_id,
            "mode": "image-to-image" if self.use_image_to_image else "text-to-image",
            "total_images": len(images),
            "requested_images": num_outputs,
        }

        return images, metadata

    def _generate_image_to_image(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        image-to-image生成（SD 3.5の主機能）
        
        衣類画像を参照画像として使用し、その衣類を着たモデルを生成
        """
        from core.pipeline.prompt_generator import PromptGenerator
        
        # プロンプト生成
        generator = PromptGenerator()
        prompts = generator.build_faithful_prompt(garments, model_attrs, config)
        
        # 最初の衣類画像を参照画像として使用
        reference_garment = garments[0]
        
        print(f"[Stability AI] Using image-to-image mode with reference: {reference_garment.image_path}")
        
        # 衣類画像を読み込み
        img = Image.open(reference_garment.image_path)
        
        # リサイズ（SD 3.5の推奨サイズ）
        max_size = 1024
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # SD 3.5 image-to-image APIエンドポイント
        url = f"{self.api_host}/v2beta/stable-image/generate/sd3"
        
        # 画像をバイトストリームに変換
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # マルチパートフォームデータ
        files = {
            "image": ("reference.png", img_byte_arr, "image/png")
        }
        
        data = {
            "prompt": prompts["prompt"],
            "negative_prompt": prompts["negative_prompt"],
            "mode": "image-to-image",
            "strength": 0.95,  # 極めて高く：参照は色・柄のヒントのみ
            "cfg_scale": 9.0,  # 高めでプロンプト遵守度UP
            "seed": config.seed if config.seed else 0,
            "output_format": "png",
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/*",
        }
        
        print(f"[Stability AI] Sending request to SD 3.5...")
        print(f"[Stability AI] Prompt: {prompts['prompt'][:100]}...")
        
        # APIリクエスト
        response = requests.post(
            url, 
            headers=headers, 
            files=files,
            data=data,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(
                f"Stability API error: {response.status_code} - {response.text}"
            )
        
        # 画像を取得（レスポンスは直接画像データ）
        generated_image = Image.open(BytesIO(response.content))
        
        print(f"[Stability AI] Image generated successfully! Size: {generated_image.size}")
        
        metadata = {
            "mode": "image-to-image",
            "reference_image": reference_garment.image_path,
            "strength": 0.98,
        }
        
        return generated_image, metadata

    def _generate_text_to_image(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        text-to-image生成（フォールバック用）
        """
        from core.pipeline.prompt_generator import PromptGenerator
        
        generator = PromptGenerator()
        prompts = generator.build_faithful_prompt(garments, model_attrs, config)
        
        # SD 3.5 text-to-image APIエンドポイント
        url = f"{self.api_host}/v2beta/stable-image/generate/sd3"
        
        data = {
            "prompt": prompts["prompt"],
            "negative_prompt": prompts["negative_prompt"],
            "mode": "text-to-image",
            "aspect_ratio": self._size_to_aspect_ratio(config.size),
            "cfg_scale": min(config.cfg_scale, 10.0),  # SD 3.5の上限は10
            "seed": config.seed if config.seed else 0,
            "output_format": "png",
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/*",
        }
        
        response = requests.post(url, headers=headers, data=data, timeout=120)
        
        if response.status_code != 200:
            raise Exception(
                f"Stability API error: {response.status_code} - {response.text}"
            )
        
        generated_image = Image.open(BytesIO(response.content))
        
        metadata = {"mode": "text-to-image"}
        
        return generated_image, metadata

    def _size_to_aspect_ratio(self, size: str) -> str:
        """サイズからアスペクト比を決定"""
        if size == "1024x1024":
            return "1:1"
        elif size == "1024x1792":
            return "9:16"
        elif size == "1792x1024":
            return "16:9"
        else:
            return "1:1"

    def check_api_status(self) -> bool:
        """API接続状態の確認"""
        try:
            url = f"{self.api_host}/v1/engines/list"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def estimate_cost(self, config: GenerationConfig) -> float:
        """
        生成コストの見積もり

        Stability AI SD 3.5の価格（2025年時点）:
        - SD 3.5 Large: $0.065/image
        - SD 3.5 Turbo: $0.040/image
        """
        # SD 3.5のコスト
        if "turbo" in self.engine_id:
            cost_per_image = 0.040
        else:
            cost_per_image = 0.065
        
        return cost_per_image * config.num_outputs

    def supports_seed(self) -> bool:
        """Stability AIはseedをサポート"""
        return True

    def supports_multi_output(self) -> bool:
        """SD 3.5は1枚ずつ生成（ループで複数枚対応）"""
        return False  # SD 3.5は1リクエスト1枚
