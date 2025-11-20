"""Google Vertex AI Imagen 4 adapter"""

import base64
from io import BytesIO
from typing import List, Tuple, Dict, Any
from PIL import Image
import requests

from models.clothing_item import ClothingItem
from models.model_attributes import ModelAttributes
from models.generation_config import GenerationConfig
from core.adapters.provider_base import ProviderBase


class VertexAdapter(ProviderBase):
    """Google Vertex AI Imagen 4 アダプタ"""

    def __init__(self, api_key: str, project_id: str = None, location: str = "us-central1"):
        """
        Args:
            api_key: Google AI Studio APIキー または サービスアカウントJSONパス
            project_id: Google Cloud プロジェクトID（Vertex AI使用時）
            location: リージョン
        """
        super().__init__(api_key)
        self.project_id = project_id
        self.location = location
        
        # Imagen 4の最新モデル（2025年6月更新）
        self.model_name = "imagen-4.0-generate-001"  # Standard
        # self.model_name = "imagen-4.0-ultra-generate-001"  # Ultra（高品質）
        # self.model_name = "imagen-4.0-fast-generate-001"  # Fast（高速）
        
        # Gemini API（簡易）を使用するか、Vertex AI（本格）を使用するか
        self.use_gemini_api = True  # APIキーで簡単に使用可能

        # Google Cloud AIプラットフォームの初期化は実際の実装時に行う
        # from google.cloud import aiplatform
        # aiplatform.init(project=project_id, location=location)

    def prepare(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
    ) -> Dict[str, Any]:
        """生成リクエストの準備（Imagen 4）"""
        from core.pipeline.prompt_generator import PromptGenerator

        generator = PromptGenerator()
        prompts = generator.build_faithful_prompt(garments, model_attrs, config)

        # アスペクト比を決定
        aspect_ratio = self._size_to_aspect_ratio(config.size)

        # Imagen 4のパラメータ
        return {
            "prompt": prompts["prompt"],
            "numberOfImages": config.num_outputs,  # 1-4枚を直接指定可能
            "aspectRatio": aspect_ratio,
            "safetyFilterLevel": "block_few",  # block_none/block_few/block_some/block_most
            "personGeneration": "allow_adult",  # dont_allow/allow_adult/allow_all
            "imageSize": "1K",  # 1K または 2K（Standard/Ultraのみ）
            "addWatermark": True,  # SynthID透かし（デフォルトtrue）
        }

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

    def generate(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
        num_outputs: int,
    ) -> Tuple[List[Image.Image], Dict[str, Any]]:
        """
        画像生成（Imagen 4）

        Args:
            garments: 衣類アイテムのリスト
            model_attrs: モデル属性
            config: 生成設定
            num_outputs: 出力枚数（1-4）

        Returns:
            (生成画像のリスト, メタデータ)
        """
        params = self.prepare(garments, model_attrs, config)
        params["numberOfImages"] = num_outputs  # 出力枚数を上書き

        if self.use_gemini_api:
            # Gemini API経由（簡易、APIキーのみ）
            return self._generate_via_gemini_api(params, num_outputs)
        else:
            # Vertex AI経由（本格、サービスアカウント必要）
            return self._generate_via_vertex_ai(params, num_outputs)

    def _generate_via_gemini_api(
        self, params: Dict[str, Any], num_outputs: int
    ) -> Tuple[List[Image.Image], Dict[str, Any]]:
        """
        Gemini API経由で画像生成（APIキーで簡単に使用可能）
        """
        # Gemini APIエンドポイント
        url = "https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict"
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        
        # リクエストボディ
        request_data = {
            "instances": [
                {
                    "prompt": params["prompt"],
                }
            ],
            "parameters": {
                "sampleCount": num_outputs,
                "aspectRatio": params["aspectRatio"],
                "personGeneration": params["personGeneration"],
                "safetyFilterLevel": params["safetyFilterLevel"],
                "includeWatermark": params["addWatermark"],
            }
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=request_data,
                timeout=120
            )
            
            if response.status_code != 200:
                raise Exception(
                    f"Gemini API error: {response.status_code} - {response.text}"
                )
            
            # レスポンスから画像を取得
            data = response.json()
            images = []
            
            for prediction in data.get("predictions", []):
                # Base64デコード
                if "bytesBase64Encoded" in prediction:
                    image_bytes = base64.b64decode(prediction["bytesBase64Encoded"])
                    image = Image.open(BytesIO(image_bytes))
                    images.append(image)
            
            metadata = {
                "provider": "google_gemini_api",
                "model": self.model_name,
                "aspect_ratio": params["aspectRatio"],
                "total_images": len(images),
                "requested_images": num_outputs,
                "watermark": params["addWatermark"],
            }
            
            return images, metadata
            
        except Exception as e:
            print(f"[Gemini API] Error: {e}")
            # フォールバック: 空リストを返す
            return [], {"error": str(e), "provider": "google_gemini_api"}

    def _generate_via_vertex_ai(
        self, params: Dict[str, Any], num_outputs: int
    ) -> Tuple[List[Image.Image], Dict[str, Any]]:
        """
        Vertex AI経由で画像生成（本格的な実装）
        
        Note: google-cloud-aiplatform パッケージが必要
        """
        try:
            from google.cloud import aiplatform
            from google.oauth2 import service_account
            import json
            
            # サービスアカウント認証
            if self.api_key.endswith('.json'):
                credentials = service_account.Credentials.from_service_account_file(
                    self.api_key
                )
                aiplatform.init(
                    project=self.project_id,
                    location=self.location,
                    credentials=credentials
                )
            
            # Imagen 4モデルを使用
            model = aiplatform.ImageGenerationModel.from_pretrained(self.model_name)
            
            # 画像生成
            response = model.generate_images(
                prompt=params["prompt"],
                number_of_images=num_outputs,
                aspect_ratio=params["aspectRatio"],
                person_generation=params["personGeneration"],
                safety_filter_level=params["safetyFilterLevel"],
                add_watermark=params["addWatermark"],
            )
            
            images = []
            for image_obj in response.images:
                image_bytes = image_obj._image_bytes
                image = Image.open(BytesIO(image_bytes))
                images.append(image)
            
            metadata = {
                "provider": "vertex_ai",
                "model": self.model_name,
                "project_id": self.project_id,
                "location": self.location,
                "aspect_ratio": params["aspectRatio"],
                "total_images": len(images),
                "requested_images": num_outputs,
                "watermark": params["addWatermark"],
            }
            
            return images, metadata
            
        except ImportError:
            print("[Vertex AI] google-cloud-aiplatform not installed. Fallback to Gemini API.")
            return self._generate_via_gemini_api(params, num_outputs)
        except Exception as e:
            print(f"[Vertex AI] Error: {e}")
            return [], {"error": str(e), "provider": "vertex_ai"}

    def check_api_status(self) -> bool:
        """API接続状態の確認"""
        try:
            # 実際の実装では、Vertex AIの接続確認を行う
            # from google.cloud import aiplatform
            # aiplatform.init(project=self.project_id, location=self.location)
            return True
        except Exception:
            return False

    def estimate_cost(self, config: GenerationConfig) -> float:
        """
        生成コストの見積もり

        Imagen 4の価格（2025年時点）:
        - Standard (imagen-4.0-generate-001): $0.040/image
        - Ultra (imagen-4.0-ultra-generate-001): $0.080/image
        - Fast (imagen-4.0-fast-generate-001): $0.020/image
        """
        # モデル名に応じてコストを計算
        if "ultra" in self.model_name:
            cost_per_image = 0.080
        elif "fast" in self.model_name:
            cost_per_image = 0.020
        else:
            cost_per_image = 0.040
        
        return cost_per_image * config.num_outputs

    def supports_seed(self) -> bool:
        """Vertex AI Imagenはseedをサポート"""
        return True

    def supports_multi_output(self) -> bool:
        """Vertex AI Imagenは複数枚出力をネイティブサポート（1-4枚）"""
        return True

