"""Clothing color change utility"""

import numpy as np
from PIL import Image
import cv2
from typing import Tuple, Optional, Dict


class ColorChanger:
    """衣類の色を変更
    
    HSV色空間を使用して、衣類の色相・彩度・明度を調整します
    """
    
    def __init__(self):
        """初期化"""
        pass
    
    def change_color(
        self,
        image: Image.Image,
        hue_shift: int = 0,
        saturation_scale: float = 1.0,
        value_scale: float = 1.0,
        mask: Optional[np.ndarray] = None
    ) -> Image.Image:
        """
        画像の色を変更
        
        Args:
            image: 入力画像
            hue_shift: 色相のシフト（-180〜180）
            saturation_scale: 彩度の倍率（0.0〜2.0）
            value_scale: 明度の倍率（0.0〜2.0）
            mask: マスク（Noneの場合は全体に適用）
        
        Returns:
            色変更後の画像
        """
        # PIL画像をNumPy配列に変換
        img_array = np.array(image.convert('RGB'))
        
        # BGR形式に変換（OpenCV用）
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # HSV色空間に変換
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # 色相をシフト
        if hue_shift != 0:
            img_hsv[:, :, 0] = (img_hsv[:, :, 0] + hue_shift) % 180
        
        # 彩度を調整
        if saturation_scale != 1.0:
            img_hsv[:, :, 1] = np.clip(img_hsv[:, :, 1] * saturation_scale, 0, 255)
        
        # 明度を調整
        if value_scale != 1.0:
            img_hsv[:, :, 2] = np.clip(img_hsv[:, :, 2] * value_scale, 0, 255)
        
        # BGR色空間に戻す
        img_hsv = img_hsv.astype(np.uint8)
        img_bgr_modified = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)
        
        # マスクを適用（指定された場合のみ）
        if mask is not None:
            mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) if len(mask.shape) == 2 else mask
            mask_3ch = mask_3ch.astype(np.float32) / 255.0
            img_bgr_modified = (img_bgr_modified * mask_3ch + img_bgr * (1 - mask_3ch)).astype(np.uint8)
        
        # RGB形式に変換
        img_rgb = cv2.cvtColor(img_bgr_modified, cv2.COLOR_BGR2RGB)
        
        # PIL画像に変換
        result_image = Image.fromarray(img_rgb)
        
        return result_image
    
    def create_mask_by_color(
        self,
        image: Image.Image,
        target_color: Tuple[int, int, int],
        tolerance: int = 30
    ) -> np.ndarray:
        """
        指定した色の領域をマスクとして抽出
        
        Args:
            image: 入力画像
            target_color: ターゲット色（RGB）
            tolerance: 色の許容範囲
        
        Returns:
            マスク（0-255の2次元配列）
        """
        # PIL画像をNumPy配列に変換
        img_array = np.array(image.convert('RGB'))
        
        # BGR形式に変換
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # HSV色空間に変換
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        
        # ターゲット色をHSVに変換
        target_bgr = np.uint8([[[target_color[2], target_color[1], target_color[0]]]])
        target_hsv = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2HSV)[0][0]
        
        # 色範囲を設定
        lower_bound = np.array([
            max(0, target_hsv[0] - tolerance),
            max(0, target_hsv[1] - tolerance),
            max(0, target_hsv[2] - tolerance)
        ])
        upper_bound = np.array([
            min(180, target_hsv[0] + tolerance),
            255,
            255
        ])
        
        # マスクを作成
        mask = cv2.inRange(img_hsv, lower_bound, upper_bound)
        
        # モルフォロジー処理でノイズ除去
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        return mask
    
    def change_to_specific_color(
        self,
        image: Image.Image,
        source_color: Tuple[int, int, int],
        target_color: Tuple[int, int, int],
        tolerance: int = 30
    ) -> Image.Image:
        """
        特定の色を別の色に変更
        
        Args:
            image: 入力画像
            source_color: 変更元の色（RGB）
            target_color: 変更先の色（RGB）
            tolerance: 色の許容範囲
        
        Returns:
            色変更後の画像
        """
        # マスクを作成
        mask = self.create_mask_by_color(image, source_color, tolerance)
        
        # 色相シフトを計算
        source_bgr = np.uint8([[[source_color[2], source_color[1], source_color[0]]]])
        source_hsv = cv2.cvtColor(source_bgr, cv2.COLOR_BGR2HSV)[0][0]
        
        target_bgr = np.uint8([[[target_color[2], target_color[1], target_color[0]]]])
        target_hsv = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2HSV)[0][0]
        
        hue_shift = int(target_hsv[0]) - int(source_hsv[0])
        
        # 色変更を適用
        result = self.change_color(
            image,
            hue_shift=hue_shift,
            mask=mask
        )
        
        return result
    
    def preset_colors(self) -> Dict[str, Tuple[int, int, int]]:
        """プリセット色の辞書を返す
        
        Returns:
            {色名: RGB値}の辞書
        """
        return {
            "赤": (255, 0, 0),
            "青": (0, 0, 255),
            "緑": (0, 255, 0),
            "黄": (255, 255, 0),
            "ピンク": (255, 192, 203),
            "紫": (128, 0, 128),
            "オレンジ": (255, 165, 0),
            "茶": (165, 42, 42),
            "白": (255, 255, 255),
            "黒": (0, 0, 0),
            "グレー": (128, 128, 128),
        }


# テスト用
if __name__ == "__main__":
    print("=" * 70)
    print("Color Changer テスト")
    print("=" * 70)
    
    # テスト画像を作成
    test_img = Image.new('RGB', (200, 200), color='red')
    
    changer = ColorChanger()
    
    # テスト1: 色相シフト
    print("\n[TEST] 色相シフト（赤→青）...")
    shifted = changer.change_color(test_img, hue_shift=120)
    print("[OK] 色相シフト完了")
    
    # テスト2: 明度変更
    print("\n[TEST] 明度変更（暗く）...")
    darker = changer.change_color(test_img, value_scale=0.5)
    print("[OK] 明度変更完了")
    
    # テスト3: 彩度変更
    print("\n[TEST] 彩度変更（鮮やか）...")
    vivid = changer.change_color(test_img, saturation_scale=1.5)
    print("[OK] 彩度変更完了")
    
    # プリセット色を表示
    print("\n[INFO] プリセット色:")
    for name, rgb in changer.preset_colors().items():
        print(f"  - {name}: RGB{rgb}")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] すべてのテスト完了")
    print("=" * 70)

