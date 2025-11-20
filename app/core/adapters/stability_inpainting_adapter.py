"""Stability AI Inpainting adapter for virtual try-on"""

import base64
from io import BytesIO
from typing import Tuple, Optional
from PIL import Image
import requests
import numpy as np


class StabilityInpaintingAdapter:
    """Stability AI Inpainting アダプター
    
    参考人物画像の服の部分だけを変更します
    """
    
    def __init__(self, api_key: str):
        """
        Args:
            api_key: Stability AI APIキー
        """
        self.api_key = api_key
        self.api_host = "https://api.stability.ai"
    
    def virtual_tryon(
        self,
        person_image: Image.Image,
        clothing_prompt: str,
        mask: Optional[Image.Image] = None,
        progress_callback=None
    ) -> Tuple[Image.Image, dict]:
        """
        バーチャル試着：人物画像の服を変更
        
        Args:
            person_image: 参考人物画像（ベース）
            clothing_prompt: 服の説明（テキスト）
            mask: 変更領域のマスク（Noneの場合は自動生成）
            progress_callback: 進捗コールバック
        
        Returns:
            (生成画像, メタデータ)
        """
        print(f"\n[Stability Inpainting] バーチャル試着開始")
        
        # 進捗報告
        if progress_callback:
            progress_callback("マスクを生成中...", 10)
        
        # マスクが指定されていない場合は自動生成
        if mask is None:
            mask = self._create_clothing_mask(person_image)
        
        # 進捗報告
        if progress_callback:
            progress_callback("Stability Inpainting APIに送信中...", 30)
        
        # Inpainting APIを呼び出し
        result_image, metadata = self._call_inpainting_api(
            person_image,
            mask,
            clothing_prompt
        )
        
        print(f"[Stability Inpainting] 完了")
        
        return result_image, metadata
    
    def _create_clothing_mask(self, person_image: Image.Image) -> Image.Image:
        """
        服の領域を自動検出してマスクを生成
        
        Args:
            person_image: 人物画像
        
        Returns:
            マスク画像（白=変更、黒=保持）
        """
        print("[Stability Inpainting] 服の領域を自動検出中...")
        
        # 簡易的なマスク生成（体の中央部分を服として扱う）
        width, height = person_image.size
        mask = Image.new('L', (width, height), 0)  # 黒
        
        # 体の中央部分を白で塗る（服の領域）
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        
        # 上半身の服（肩から腰まで）
        top_start_y = int(height * 0.2)   # 肩
        top_end_y = int(height * 0.6)     # 腰
        left_x = int(width * 0.2)
        right_x = int(width * 0.8)
        
        draw.rectangle(
            [(left_x, top_start_y), (right_x, top_end_y)],
            fill=255  # 白
        )
        
        # 下半身の服（腰から足首まで）- オプション
        bottom_start_y = int(height * 0.5)
        bottom_end_y = int(height * 0.85)
        
        draw.rectangle(
            [(left_x, bottom_start_y), (right_x, bottom_end_y)],
            fill=255
        )
        
        print(f"[Stability Inpainting] マスク生成完了")
        
        return mask
    
    def _call_inpainting_api(
        self,
        image: Image.Image,
        mask: Image.Image,
        prompt: str
    ) -> Tuple[Image.Image, dict]:
        """
        Stability AI Inpainting APIを呼び出し
        
        Args:
            image: ベース画像
            mask: マスク画像
            prompt: プロンプト
        
        Returns:
            (生成画像, メタデータ)
        """
        url = f"{self.api_host}/v2beta/stable-image/edit/inpaint"
        
        # 画像をPNGバイト列に変換
        image_bytes = BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        
        mask_bytes = BytesIO()
        mask.save(mask_bytes, format='PNG')
        mask_bytes.seek(0)
        
        # マルチパートフォームデータ
        files = {
            "image": ("image.png", image_bytes, "image/png"),
            "mask": ("mask.png", mask_bytes, "image/png"),
        }
        
        data = {
            "prompt": prompt,
            "output_format": "png",
            "grow_mask": 5  # マスクを少し拡大（自然な境界のため）
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/*"
        }
        
        print(f"[Stability Inpainting] APIリクエスト送信...")
        print(f"[Stability Inpainting] Prompt: {prompt[:100]}...")
        
        response = requests.post(
            url,
            headers=headers,
            files=files,
            data=data,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(
                f"Stability Inpainting API error: {response.status_code} - {response.text}"
            )
        
        # 画像を取得
        result_image = Image.open(BytesIO(response.content))
        
        print(f"[Stability Inpainting] 画像生成成功")
        
        metadata = {
            "provider": "stability_inpainting",
            "method": "inpaint",
            "prompt": prompt
        }
        
        return result_image, metadata


# テスト用
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # テスト用APIキー
    TEST_API_KEY = "sk-IiO8gDGVp0ioHnrZHctNMFlI5gGNouo72m548qgC11pOJPet"
    
    print("=" * 70)
    print("Stability Inpainting Adapter テスト")
    print("=" * 70)
    
    adapter = StabilityInpaintingAdapter(TEST_API_KEY)
    
    # テスト画像
    test_person = Path("verification/virtual_tryon_result_1.png")
    
    if not test_person.exists():
        print(f"[ERROR] テスト画像が見つかりません: {test_person}")
        sys.exit(1)
    
    # 画像を読み込み
    person_img = Image.open(test_person)
    print(f"\n[TEST] 参考人物画像: {test_person}")
    print(f"  サイズ: {person_img.size}")
    
    try:
        # バーチャル試着を実行
        result, metadata = adapter.virtual_tryon(
            person_image=person_img,
            clothing_prompt="wearing a red leather jacket"
        )
        
        # 結果を保存
        output_path = "verification/inpainting_test_output.png"
        result.save(output_path)
        
        print(f"\n[SUCCESS] テスト完了")
        print(f"  出力: {output_path}")
        print(f"  メタデータ: {metadata}")
    
    except Exception as e:
        print(f"\n[ERROR] テストエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

