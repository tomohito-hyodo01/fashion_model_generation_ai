"""Face swapping utility for reference person feature"""

import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple


class FaceSwapper:
    """顔交換ユーティリティ
    
    参考人物の顔を、生成された画像に移植します
    """
    
    def __init__(self):
        """初期化"""
        pass
    
    def swap_face(
        self,
        source_image: Image.Image,  # 参考人物（顔のソース）
        target_image: Image.Image,  # 生成画像（体のソース）
    ) -> Image.Image:
        """
        顔を交換
        
        Args:
            source_image: 参考人物画像（この顔を使用）
            target_image: 生成画像（この体を使用）
        
        Returns:
            顔交換後の画像
        """
        print("[Face Swapper] 顔交換を開始...")
        
        # PIL → OpenCV形式に変換
        source_cv = cv2.cvtColor(np.array(source_image.convert('RGB')), cv2.COLOR_RGB2BGR)
        target_cv = cv2.cvtColor(np.array(target_image.convert('RGB')), cv2.COLOR_RGB2BGR)
        
        # 顔検出
        source_face_box = self._detect_face(source_cv)
        target_face_box = self._detect_face(target_cv)
        
        if source_face_box is None or target_face_box is None:
            print("[Face Swapper] 顔が検出できませんでした。元の画像を返します。")
            return target_image
        
        # 顔を抽出
        sx1, sy1, sx2, sy2 = source_face_box
        tx1, ty1, tx2, ty2 = target_face_box
        
        source_face = source_cv[sy1:sy2, sx1:sx2]
        
        # ターゲットサイズにリサイズ
        target_width = tx2 - tx1
        target_height = ty2 - ty1
        resized_face = cv2.resize(source_face, (target_width, target_height))
        
        # 顔を貼り付け
        result_cv = target_cv.copy()
        result_cv[ty1:ty2, tx1:tx2] = resized_face
        
        # ぼかして境界を自然に
        result_cv = self._blend_face(result_cv, target_cv, target_face_box)
        
        # OpenCV → PIL形式に変換
        result_rgb = cv2.cvtColor(result_cv, cv2.COLOR_BGR2RGB)
        result_image = Image.fromarray(result_rgb)
        
        print("[Face Swapper] 顔交換完了")
        
        return result_image
    
    def _detect_face(self, image_cv: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        顔を検出
        
        Args:
            image_cv: OpenCV形式の画像
        
        Returns:
            (x1, y1, x2, y2) または None
        """
        # Haar Cascade分類器で顔検出
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return None
        
        # 最も大きい顔を使用
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = largest_face
        
        # 顔の領域を少し拡大（髪や首も含める）
        expand = 0.3
        x1 = max(0, int(x - w * expand))
        y1 = max(0, int(y - h * expand * 1.5))  # 上は髪があるので more
        x2 = min(image_cv.shape[1], int(x + w * (1 + expand)))
        y2 = min(image_cv.shape[0], int(y + h * (1 + expand * 0.5)))
        
        return (x1, y1, x2, y2)
    
    def _blend_face(
        self,
        result: np.ndarray,
        original: np.ndarray,
        face_box: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """
        顔の境界をぼかして自然に
        
        Args:
            result: 顔交換後の画像
            original: 元の画像
            face_box: 顔の領域
        
        Returns:
            ぼかし処理後の画像
        """
        x1, y1, x2, y2 = face_box
        
        # マスクを作成（中心が1、端が0）
        mask = np.zeros((y2 - y1, x2 - x1), dtype=np.float32)
        center_x = (x2 - x1) // 2
        center_y = (y2 - y1) // 2
        
        for y in range(y2 - y1):
            for x in range(x2 - x1):
                dist_x = abs(x - center_x) / center_x
                dist_y = abs(y - center_y) / center_y
                dist = np.sqrt(dist_x**2 + dist_y**2)
                mask[y, x] = max(0, 1 - dist)
        
        # マスクを3チャンネルに
        mask_3ch = cv2.merge([mask, mask, mask])
        
        # ブレンド
        face_region = result[y1:y2, x1:x2].astype(np.float32)
        orig_region = original[y1:y2, x1:x2].astype(np.float32)
        
        blended = (face_region * mask_3ch + orig_region * (1 - mask_3ch)).astype(np.uint8)
        
        result_blended = result.copy()
        result_blended[y1:y2, x1:x2] = blended
        
        return result_blended


# テスト用
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    print("=" * 70)
    print("Face Swapper テスト")
    print("=" * 70)
    
    swapper = FaceSwapper()
    
    # テスト画像
    test_source = Path("verification/virtual_tryon_result_1.png")
    test_target = Path("verification/generated_1.png")
    
    if not test_source.exists() or not test_target.exists():
        print(f"[ERROR] テスト画像が見つかりません")
        sys.exit(1)
    
    # 画像を読み込み
    source_img = Image.open(test_source)
    target_img = Image.open(test_target)
    
    print(f"\n[TEST] ソース（顔の元）: {test_source}")
    print(f"[TEST] ターゲット（体の元）: {test_target}")
    
    try:
        # 顔交換を実行
        result = swapper.swap_face(source_img, target_img)
        
        # 結果を保存
        output_path = "verification/face_swap_test_output.png"
        result.save(output_path)
        
        print(f"\n[SUCCESS] テスト完了")
        print(f"  出力: {output_path}")
    
    except Exception as e:
        print(f"\n[ERROR] テストエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

