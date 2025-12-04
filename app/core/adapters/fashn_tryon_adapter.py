"""FASHN AI Virtual Try-On adapter"""

import base64
import time
from io import BytesIO
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from PIL import Image
import requests


class FashnTryonAdapter:
    """FASHN AI Virtual Try-On アダプター
    
    参考人物に衣類を着せる専用API
    """
    
    def __init__(self, api_key: str):
        """
        Args:
            api_key: FASHN AI APIキー
        """
        self.api_key = api_key
        self.base_url = "https://api.fashn.ai/v1"
        self.run_endpoint = f"{self.base_url}/run"
        self.status_endpoint = f"{self.base_url}/status"
        # FASHN Virtual Try-On v1.6モデル（正しいmodel_name）
        self.model_name = "tryon-v1.6"
    
    def encode_image_to_base64(self, image: Image.Image) -> str:
        """PIL画像をBase64（data URL形式）に変換"""
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        
        b64 = base64.b64encode(buffer.getvalue()).decode('ascii')
        data_url = f"data:image/png;base64,{b64}"
        
        return data_url
    
    def virtual_tryon(
        self,
        person_image: Image.Image,
        garment_image: Image.Image,
        category: str = "auto",
        garment_photo_type: str = "flat-lay",
        mode: str = "quality",
        num_samples: int = 1,
        progress_callback=None
    ) -> Tuple[List[Image.Image], Dict]:
        """
        バーチャル試着
        
        Args:
            person_image: 参考人物画像
            garment_image: 衣類画像
            category: 衣類カテゴリー（auto/tops/bottoms/one-pieces）
            garment_photo_type: 衣類画像タイプ（auto/flat-lay/model）
            mode: 処理モード（performance/balanced/quality）
            num_samples: 生成枚数（1-4）
            progress_callback: 進捗コールバック
        
        Returns:
            (生成画像リスト, メタデータ)
        """
        print(f"\n[FASHN Try-On] バーチャル試着開始")
        print(f"  category: {category}")
        print(f"  num_samples: {num_samples}")
        
        # 進捗報告
        if progress_callback:
            progress_callback("画像をエンコード中...", 10)
        
        # 画像をBase64エンコード
        person_data_url = self.encode_image_to_base64(person_image)
        garment_data_url = self.encode_image_to_base64(garment_image)
        
        # 進捗報告
        if progress_callback:
            progress_callback("バーチャル試着ジョブを作成中...", 20)
        
        # 予測ジョブを作成
        prediction_id = self._create_tryon_prediction(
            person_data_url,
            garment_data_url,
            category,
            garment_photo_type,
            mode,
            num_samples
        )
        
        print(f"[FASHN Try-On] prediction_id: {prediction_id}")
        
        # 進捗報告
        if progress_callback:
            progress_callback("試着画像を生成中...", 30)
        
        # ステータスをポーリング
        image_urls, metadata = self._poll_status(
            prediction_id,
            poll_interval=5,
            timeout=300,
            progress_callback=progress_callback
        )
        
        # 画像をダウンロード
        if progress_callback:
            progress_callback("画像をダウンロード中...", 90)
        
        images = []
        for url in image_urls:
            img = self._download_image(url)
            images.append(img)
        
        print(f"[FASHN Try-On] 完了: {len(images)}枚生成")
        
        return images, metadata
    
    def _create_tryon_prediction(
        self,
        person_data_url: str,
        garment_data_url: str,
        category: str,
        garment_photo_type: str,
        mode: str,
        num_samples: int
    ) -> str:
        """Try-On予測ジョブを作成"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        inputs = {
            "model_image": person_data_url,           # 参考人物画像
            "garment_image": garment_data_url,        # 衣類画像
            "category": category,                     # auto/tops/bottoms/one-pieces
            "garment_photo_type": garment_photo_type, # auto/flat-lay/model
            "mode": mode,                             # performance/balanced/quality
            "segmentation_free": True,                # 元の服を自動除去
            "moderation_level": "permissive",         # コンテンツモデレーション
            "num_samples": num_samples,               # 生成枚数
            "output_format": "png",                   # 出力形式
        }
        
        payload = {
            "model_name": self.model_name,
            "inputs": inputs,
        }
        
        try:
            resp = requests.post(
                self.run_endpoint,
                json=payload,
                headers=headers,
                timeout=60
            )
            resp.raise_for_status()
            data = resp.json()
            
            if data.get("error"):
                raise RuntimeError(f"FASHN API error: {data['error']}")
            
            prediction_id = data.get("id")
            if not prediction_id:
                raise RuntimeError(f"予測IDがレスポンスに含まれていません: {data}")
            
            return prediction_id
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"FASHN API リクエストエラー: {e}")
    
    def _poll_status(
        self,
        prediction_id: str,
        poll_interval: int,
        timeout: int,
        progress_callback=None
    ) -> Tuple[List[str], Dict]:
        """ステータスをポーリング"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        status_url = f"{self.status_endpoint}/{prediction_id}"
        
        start_time = time.time()
        poll_count = 0
        
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > timeout:
                raise TimeoutError(f"試着処理がタイムアウトしました (>{timeout}秒)")
            
            poll_count += 1
            
            try:
                resp = requests.get(status_url, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                
                status = data.get("status")
                error = data.get("error")
                
                print(f"[FASHN Try-On] ポーリング #{poll_count}: status={status}")
                
                # 進捗報告
                if progress_callback:
                    progress = 30 + min(int(elapsed / timeout * 60), 60)
                    progress_callback(f"試着処理中... ({status})", progress)
                
                # 完了
                if status == "completed":
                    outputs = data.get("output") or []
                    if not outputs:
                        raise RuntimeError("画像URLが取得できませんでした")
                    
                    metadata = {
                        "provider": "fashn_tryon",
                        "prediction_id": prediction_id,
                        "status": status,
                        "elapsed_time": int(elapsed)
                    }
                    
                    return outputs, metadata
                
                # 失敗
                if status == "failed":
                    raise RuntimeError(f"試着処理が失敗しました: {error}")
                
                # 処理中の場合は待機
                time.sleep(poll_interval)
            
            except requests.exceptions.RequestException as e:
                print(f"[FASHN Try-On] ポーリングエラー: {e}")
                time.sleep(poll_interval)
                continue
    
    def _download_image(self, image_url: str) -> Image.Image:
        """画像をダウンロード"""
        try:
            resp = requests.get(image_url, timeout=60)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content))
            return img
        except Exception as e:
            raise RuntimeError(f"画像ダウンロードエラー: {e}")


# テスト用
if __name__ == "__main__":
    import sys
    import os

    # テスト用APIキー（環境変数から取得）
    TEST_API_KEY = os.environ.get("FASHN_API_KEY", "")
    if not TEST_API_KEY:
        print("環境変数 FASHN_API_KEY を設定してください")
        sys.exit(1)

    print("=" * 70)
    print("FASHN Virtual Try-On Adapter テスト")
    print("=" * 70)

    adapter = FashnTryonAdapter(TEST_API_KEY)
    
    # テスト画像
    test_person = Path("verification/virtual_tryon_result_1.png")
    test_garment = Path("verification/sample_tshirt.png")
    
    if not test_person.exists() or not test_garment.exists():
        print(f"[ERROR] テスト画像が見つかりません")
        sys.exit(1)
    
    # 画像を読み込み
    person_img = Image.open(test_person)
    garment_img = Image.open(test_garment)
    
    print(f"\n[TEST] 参考人物: {test_person}")
    print(f"[TEST] 衣類: {test_garment}")
    
    try:
        # バーチャル試着を実行
        images, metadata = adapter.virtual_tryon(
            person_image=person_img,
            garment_image=garment_img,
            category="auto",
            garment_photo_type="flat-lay",
            mode="quality",
            num_samples=1
        )
        
        # 結果を保存
        for i, img in enumerate(images):
            output_path = f"verification/fashn_tryon_output_{i+1}.png"
            img.save(output_path)
            print(f"[SUCCESS] 保存: {output_path}")
        
        print(f"\n[SUCCESS] テスト完了")
        print(f"  生成枚数: {len(images)}")
        print(f"  メタデータ: {metadata}")
    
    except Exception as e:
        print(f"\n[ERROR] テストエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

