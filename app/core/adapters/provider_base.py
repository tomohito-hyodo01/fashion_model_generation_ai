"""Base class for all image generation providers"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any
from PIL import Image

from models.clothing_item import ClothingItem
from models.model_attributes import ModelAttributes
from models.generation_config import GenerationConfig


class ProviderBase(ABC):
    """API連携の基底クラス"""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: API認証キー
        """
        self.api_key = api_key

    @abstractmethod
    def prepare(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
    ) -> Dict[str, Any]:
        """
        生成リクエストの準備

        Args:
            garments: 衣類アイテムのリスト
            model_attrs: モデル属性
            config: 生成設定

        Returns:
            準備されたリクエストパラメータ
        """
        pass

    @abstractmethod
    def generate(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
        num_outputs: int,
    ) -> Tuple[List[Image.Image], Dict[str, Any]]:
        """
        画像生成

        Args:
            garments: 衣類アイテムのリスト
            model_attrs: モデル属性
            config: 生成設定
            num_outputs: 出力枚数（1-4）

        Returns:
            (生成画像のリスト, メタデータ)
        """
        pass

    @abstractmethod
    def check_api_status(self) -> bool:
        """
        API接続状態の確認

        Returns:
            接続可能ならTrue
        """
        pass

    @abstractmethod
    def estimate_cost(self, config: GenerationConfig) -> float:
        """
        生成コストの見積もり

        Args:
            config: 生成設定

        Returns:
            推定コスト（USD）
        """
        pass

    @abstractmethod
    def supports_seed(self) -> bool:
        """
        Seed固定をサポートするか

        Returns:
            サポートする場合True
        """
        pass

    def supports_multi_output(self) -> bool:
        """
        複数枚出力をネイティブサポートするか

        Returns:
            サポートする場合True（デフォルトはFalse）
        """
        return False

