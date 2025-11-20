"""Tests for data models"""

import pytest
from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from models.clothing_item import ClothingItem
from models.model_attributes import ModelAttributes
from models.generation_config import GenerationConfig


class TestClothingItem:
    """ClothingItem のテスト"""

    def test_valid_creation(self, tmp_path):
        """有効なClothingItemの作成"""
        # テスト用の画像を作成
        img_path = tmp_path / "test.png"
        img_path.touch()

        item = ClothingItem(image_path=str(img_path), clothing_type="TOP")

        assert item.image_path == str(img_path)
        assert item.clothing_type == "TOP"

    def test_invalid_clothing_type(self, tmp_path):
        """無効な衣類タイプでエラー"""
        img_path = tmp_path / "test.png"
        img_path.touch()

        with pytest.raises(ValueError):
            ClothingItem(image_path=str(img_path), clothing_type="INVALID")

    def test_missing_image_file(self):
        """存在しない画像ファイルでエラー"""
        with pytest.raises(ValueError):
            ClothingItem(image_path="nonexistent.png", clothing_type="TOP")


class TestModelAttributes:
    """ModelAttributes のテスト"""

    def test_valid_creation(self):
        """有効なModelAttributesの作成"""
        attrs = ModelAttributes(
            gender="female",
            age_range="20s",
            ethnicity="asian",
            body_type="slim",
        )

        assert attrs.gender == "female"
        assert attrs.age_range == "20s"

    def test_invalid_gender(self):
        """無効な性別でエラー"""
        with pytest.raises(ValueError):
            ModelAttributes(gender="invalid")

    def test_to_description(self):
        """プロンプト用描写の生成"""
        attrs = ModelAttributes(
            gender="female",
            age_range="20s",
            ethnicity="asian",
            body_type="slim",
            pose="front",
        )

        desc = attrs.to_description()

        assert "20s female" in desc
        assert "asian" in desc
        assert "slim" in desc


class TestGenerationConfig:
    """GenerationConfig のテスト"""

    def test_valid_creation(self):
        """有効なGenerationConfigの作成"""
        config = GenerationConfig(provider="openai", num_outputs=2)

        assert config.provider == "openai"
        assert config.num_outputs == 2

    def test_invalid_provider(self):
        """無効なプロバイダでエラー"""
        with pytest.raises(ValueError):
            GenerationConfig(provider="invalid")

    def test_invalid_num_outputs(self):
        """無効な出力枚数でエラー"""
        with pytest.raises(ValueError):
            GenerationConfig(provider="openai", num_outputs=5)  # 1-4のみ有効

    def test_cfg_scale_validation(self):
        """cfg_scaleの範囲チェック"""
        with pytest.raises(ValueError):
            GenerationConfig(provider="stability", cfg_scale=20.0)  # 7-15のみ有効

