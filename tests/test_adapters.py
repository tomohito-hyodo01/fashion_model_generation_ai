"""Tests for API adapters"""

import pytest
from unittest.mock import Mock, patch
from PIL import Image

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from models.clothing_item import ClothingItem
from models.model_attributes import ModelAttributes
from models.generation_config import GenerationConfig
from core.adapters.openai_adapter import OpenAIAdapter
from core.adapters.stability_adapter import StabilityAdapter
from core.adapters.vertex_adapter import VertexAdapter


class TestOpenAIAdapter:
    """OpenAI アダプタのテスト"""

    def test_supports_seed(self):
        """DALL-E 3はseedをサポートしない"""
        adapter = OpenAIAdapter("test_key")
        assert adapter.supports_seed() is False

    def test_supports_multi_output(self):
        """DALL-E 3は複数出力をネイティブサポートしない"""
        adapter = OpenAIAdapter("test_key")
        assert adapter.supports_multi_output() is False

    def test_estimate_cost(self):
        """コスト見積もりのテスト"""
        adapter = OpenAIAdapter("test_key")

        # 標準品質 1024x1024
        config = GenerationConfig(provider="openai", quality="standard", num_outputs=1)
        assert adapter.estimate_cost(config) == 0.040

        # HD品質 1024x1024
        config = GenerationConfig(provider="openai", quality="hd", num_outputs=2)
        assert adapter.estimate_cost(config) == 0.160  # 0.080 * 2


class TestStabilityAdapter:
    """Stability AI アダプタのテスト"""

    def test_supports_seed(self):
        """Stability AIはseedをサポート"""
        adapter = StabilityAdapter("test_key")
        assert adapter.supports_seed() is True

    def test_supports_multi_output(self):
        """Stability AIは複数出力をネイティブサポート"""
        adapter = StabilityAdapter("test_key")
        assert adapter.supports_multi_output() is True

    def test_estimate_cost(self):
        """コスト見積もりのテスト"""
        adapter = StabilityAdapter("test_key")

        config = GenerationConfig(provider="stability", num_outputs=3)
        assert adapter.estimate_cost(config) == 0.090  # 0.030 * 3


class TestVertexAdapter:
    """Vertex AI アダプタのテスト"""

    def test_supports_seed(self):
        """Vertex AIはseedをサポート"""
        adapter = VertexAdapter("test_key", project_id="test-project")
        assert adapter.supports_seed() is True

    def test_supports_multi_output(self):
        """Vertex AIは複数出力をネイティブサポート"""
        adapter = VertexAdapter("test_key", project_id="test-project")
        assert adapter.supports_multi_output() is True

    def test_size_to_aspect_ratio(self):
        """サイズからアスペクト比への変換"""
        adapter = VertexAdapter("test_key", project_id="test-project")

        assert adapter._size_to_aspect_ratio("1024x1024") == "1:1"
        assert adapter._size_to_aspect_ratio("1024x1792") == "9:16"
        assert adapter._size_to_aspect_ratio("1792x1024") == "16:9"

