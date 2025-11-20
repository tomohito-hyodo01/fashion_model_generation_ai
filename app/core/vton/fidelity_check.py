"""Fidelity checking for generated images"""

from typing import Dict
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import cv2


class FidelityChecker:
    """忠実度検証クラス"""

    def __init__(
        self,
        ssim_threshold: float = 0.85,
        color_hist_threshold: float = 0.90,
        keypoint_threshold: float = 0.80,
    ):
        """
        Args:
            ssim_threshold: SSIM閾値
            color_hist_threshold: 色ヒストグラム相関閾値
            keypoint_threshold: Keypoint一致閾値
        """
        self.ssim_threshold = ssim_threshold
        self.color_hist_threshold = color_hist_threshold
        self.keypoint_threshold = keypoint_threshold

    def evaluate(self, original_path: str, generated: Image.Image) -> Dict[str, float]:
        """
        忠実度指標を計算

        Args:
            original_path: 元の衣類画像パス
            generated: 生成された画像

        Returns:
            各指標のスコア辞書
        """
        try:
            # 元画像を読み込み（日本語パス対応）
            original = Image.open(original_path)
        except Exception as e:
            print(f"Warning: Failed to load original image for comparison: {e}")
            # デフォルトスコアを返す
            return {"ssim": 0.0, "color_hist": 0.0, "keypoint": 0.0}

        # 同じサイズにリサイズ
        if original.size != generated.size:
            original = original.resize(generated.size, Image.Resampling.LANCZOS)

        # numpy配列に変換
        orig_array = np.array(original.convert("RGB"))
        gen_array = np.array(generated.convert("RGB"))

        scores = {
            "ssim": self._calculate_ssim(orig_array, gen_array),
            "color_hist": self._calculate_color_hist_correlation(orig_array, gen_array),
            "keypoint": self._calculate_keypoint_match(orig_array, gen_array),
        }

        return scores

    def pass_all(self, scores: Dict[str, float]) -> bool:
        """
        全指標が閾値を満たすか

        Args:
            scores: 各指標のスコア

        Returns:
            全て合格ならTrue
        """
        return (
            scores.get("ssim", 0) >= self.ssim_threshold
            and scores.get("color_hist", 0) >= self.color_hist_threshold
            and scores.get("keypoint", 0) >= self.keypoint_threshold
        )

    def generate_heatmap(
        self, original_path: str, generated: Image.Image
    ) -> Image.Image:
        """
        差分ヒートマップを生成

        Args:
            original_path: 元の衣類画像パス
            generated: 生成された画像

        Returns:
            差分ヒートマップ画像
        """
        try:
            original = Image.open(original_path)
        except Exception as e:
            print(f"Warning: Failed to load original image for heatmap: {e}")
            # エラー時は生成画像をそのまま返す
            return generated

        if original.size != generated.size:
            original = original.resize(generated.size, Image.Resampling.LANCZOS)

        orig_array = np.array(original.convert("RGB"))
        gen_array = np.array(generated.convert("RGB"))

        # 差分を計算
        diff = np.abs(orig_array.astype(float) - gen_array.astype(float))
        diff_normalized = (diff / diff.max() * 255).astype(np.uint8)

        # ヒートマップに変換（グレースケール→カラーマップ）
        diff_gray = np.mean(diff_normalized, axis=2).astype(np.uint8)
        heatmap = cv2.applyColorMap(diff_gray, cv2.COLORMAP_JET)
        heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

        return Image.fromarray(heatmap_rgb)

    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """SSIM（構造類似度指数）を計算"""
        # グレースケールに変換
        gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)

        # SSIMを計算
        score, _ = ssim(gray1, gray2, full=True)
        return float(score)

    def _calculate_color_hist_correlation(
        self, img1: np.ndarray, img2: np.ndarray
    ) -> float:
        """色ヒストグラム相関を計算"""
        # 各チャンネルのヒストグラムを計算
        correlations = []

        for channel in range(3):  # RGB
            hist1 = cv2.calcHist([img1], [channel], None, [256], [0, 256])
            hist2 = cv2.calcHist([img2], [channel], None, [256], [0, 256])

            # 正規化
            hist1 = cv2.normalize(hist1, hist1).flatten()
            hist2 = cv2.normalize(hist2, hist2).flatten()

            # 相関係数を計算
            correlation = cv2.compareHist(
                hist1.reshape(-1, 1), hist2.reshape(-1, 1), cv2.HISTCMP_CORREL
            )
            correlations.append(correlation)

        # 平均を返す
        return float(np.mean(correlations))

    def _calculate_keypoint_match(
        self, img1: np.ndarray, img2: np.ndarray
    ) -> float:
        """柄Keypoint一致度を計算"""
        # グレースケールに変換
        gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)

        # ORB検出器を使用（SIFTより高速）
        orb = cv2.ORB_create(nfeatures=500)

        # Keypointと記述子を検出
        kp1, des1 = orb.detectAndCompute(gray1, None)
        kp2, des2 = orb.detectAndCompute(gray2, None)

        if des1 is None or des2 is None or len(kp1) == 0 or len(kp2) == 0:
            return 0.0

        # BFMatcherでマッチング
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)

        # マッチング率を計算
        match_ratio = len(matches) / max(len(kp1), len(kp2))
        return float(match_ratio)

