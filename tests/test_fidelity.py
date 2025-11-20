"""Tests for fidelity checker"""

import pytest
import numpy as np
from PIL import Image
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from core.vton.fidelity_check import FidelityChecker


class TestFidelityChecker:
    """忠実度チェッカーのテスト"""

    @pytest.fixture
    def checker(self):
        """テスト用のチェッカーインスタンス"""
        return FidelityChecker()

    @pytest.fixture
    def sample_image(self, tmp_path):
        """テスト用のサンプル画像"""
        # 青い画像を生成
        img = Image.new("RGB", (512, 512), color=(0, 0, 255))
        img_path = tmp_path / "test.png"
        img.save(img_path)
        return str(img_path)

    def test_ssim_identical_images(self, checker, sample_image):
        """同一画像のSSIMは1.0に近い"""
        original_img = Image.open(sample_image)
        scores = checker.evaluate(sample_image, original_img)

        # 同一画像なのでSSIMは1.0に近い
        assert scores["ssim"] >= 0.99

    def test_ssim_different_images(self, checker, sample_image, tmp_path):
        """異なる画像のSSIMは低い"""
        # 赤い画像を生成（元は青）
        different_img = Image.new("RGB", (512, 512), color=(255, 0, 0))

        scores = checker.evaluate(sample_image, different_img)

        # 全く異なる色なのでSSIMは低い
        assert scores["ssim"] < 0.5

    def test_pass_all_with_good_scores(self, checker):
        """閾値を満たすスコアはpass_allでTrue"""
        good_scores = {"ssim": 0.90, "color_hist": 0.95, "keypoint": 0.85}
        assert checker.pass_all(good_scores) is True

    def test_pass_all_with_bad_scores(self, checker):
        """閾値を満たさないスコアはpass_allでFalse"""
        bad_scores = {
            "ssim": 0.70,  # 閾値0.85未満
            "color_hist": 0.95,
            "keypoint": 0.85,
        }
        assert checker.pass_all(bad_scores) is False

    def test_generate_heatmap(self, checker, sample_image):
        """ヒートマップ生成のテスト"""
        original_img = Image.open(sample_image)
        heatmap = checker.generate_heatmap(sample_image, original_img)

        assert isinstance(heatmap, Image.Image)
        assert heatmap.size == original_img.size

