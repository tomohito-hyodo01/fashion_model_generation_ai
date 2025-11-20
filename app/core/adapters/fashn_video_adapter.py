"""FASHN AI video generation adapter"""

import base64
import mimetypes
import time
from io import BytesIO
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from PIL import Image
import requests


class FashnVideoAdapter:
    """FASHN AI image-to-video アダプター
    
    静止画から動画を生成します
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
        self.model_name = "image-to-video"
    
    def encode_image_to_base64(self, image: Image.Image) -> str:
        """
        PIL画像をBase64（data URL形式）に変換
        
        Args:
            image: PIL画像
        
        Returns:
            data URL形式の文字列
        """
        # PIL画像をバイト列に変換
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Base64エンコード
        b64 = base64.b64encode(buffer.getvalue()).decode('ascii')
        
        # data URL形式
        data_url = f"data:image/png;base64,{b64}"
        
        return data_url
    
    def generate_video(
        self,
        image: Image.Image,
        duration: int = 10,
        resolution: str = "1080p",
        prompt: Optional[str] = None,
        poll_interval: int = 5,
        timeout: int = 300,
        progress_callback: Optional[callable] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        画像から動画を生成
        
        Args:
            image: 入力画像（PIL Image）
            duration: 動画の長さ（5 or 10秒）
            resolution: 解像度（480p/720p/1080p）
            prompt: 動きのガイド（オプション）
            poll_interval: ポーリング間隔（秒）
            timeout: タイムアウト（秒）
            progress_callback: 進捗コールバック関数
        
        Returns:
            (動画URL, メタデータ)
        """
        print(f"\n[FASHN Video] 動画生成開始")
        print(f"  duration: {duration}秒")
        print(f"  resolution: {resolution}")
        print(f"  prompt: {prompt or '(デフォルト自動モーション)'}")
        
        # 進捗報告
        if progress_callback:
            progress_callback("画像をエンコード中...", 10)
        
        # 画像をBase64エンコード
        image_data_url = self.encode_image_to_base64(image)
        
        # 進捗報告
        if progress_callback:
            progress_callback("動画生成ジョブを作成中...", 20)
        
        # 予測ジョブを作成
        prediction_id = self._create_prediction(
            image_data_url,
            duration,
            resolution,
            prompt
        )
        
        print(f"[FASHN Video] prediction_id: {prediction_id}")
        
        # 進捗報告
        if progress_callback:
            progress_callback("動画生成を待機中...", 30)
        
        # ステータスをポーリング
        video_url, metadata = self._poll_status(
            prediction_id,
            poll_interval,
            timeout,
            progress_callback
        )
        
        print(f"[FASHN Video] 動画生成完了: {video_url}")
        
        return video_url, metadata
    
    def _create_prediction(
        self,
        image_data_url: str,
        duration: int,
        resolution: str,
        prompt: Optional[str]
    ) -> str:
        """予測ジョブを作成"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        inputs = {
            "image": image_data_url,
            "duration": duration,
            "resolution": resolution,
        }
        
        # プロンプトがある場合は追加
        if prompt:
            inputs["prompt"] = prompt
        
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
        progress_callback: Optional[callable] = None
    ) -> Tuple[str, Dict]:
        """ステータスをポーリング"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        status_url = f"{self.status_endpoint}/{prediction_id}"
        
        start_time = time.time()
        poll_count = 0
        
        while True:
            elapsed = time.time() - start_time
            
            # タイムアウトチェック
            if elapsed > timeout:
                raise TimeoutError(f"動画生成がタイムアウトしました (>{timeout}秒)")
            
            poll_count += 1
            
            try:
                resp = requests.get(status_url, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                
                status = data.get("status")
                error = data.get("error")
                
                print(f"[FASHN Video] ポーリング #{poll_count}: status={status}")
                
                # 進捗報告（30%から90%まで）
                if progress_callback:
                    progress = 30 + min(int(elapsed / timeout * 60), 60)
                    progress_callback(f"動画生成中... ({status})", progress)
                
                # 完了
                if status == "completed":
                    outputs = data.get("output") or []
                    if not outputs:
                        raise RuntimeError("動画URLが取得できませんでした")
                    
                    video_url = outputs[0]
                    
                    metadata = {
                        "provider": "fashn",
                        "prediction_id": prediction_id,
                        "status": status,
                        "duration": data.get("duration", 0),
                        "elapsed_time": int(elapsed)
                    }
                    
                    return video_url, metadata
                
                # 失敗
                if status == "failed":
                    raise RuntimeError(f"動画生成が失敗しました: {error}")
                
                # 処理中の場合は待機
                time.sleep(poll_interval)
            
            except requests.exceptions.RequestException as e:
                print(f"[FASHN Video] ポーリングエラー: {e}")
                time.sleep(poll_interval)
                continue
    
    def download_video(self, video_url: str, output_path: str) -> bool:
        """
        動画をダウンロード
        
        Args:
            video_url: 動画URL
            output_path: 保存先パス
        
        Returns:
            成功した場合はTrue
        """
        try:
            print(f"[FASHN Video] 動画をダウンロード中: {video_url}")
            
            with requests.get(video_url, stream=True, timeout=300) as r:
                r.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            
            file_size_mb = Path(output_path).stat().st_size / (1024 * 1024)
            print(f"[FASHN Video] ダウンロード完了: {output_path} ({file_size_mb:.2f} MB)")
            
            return True
        
        except Exception as e:
            print(f"[FASHN Video] ダウンロードエラー: {e}")
            return False


# テスト用
if __name__ == "__main__":
    import sys
    
    # テスト用APIキー
    TEST_API_KEY = "fa-uCRCpnOMl0uK-ylgH33BqyMDdtVyiEZ9SDRLo"
    
    print("=" * 70)
    print("FASHN Video Adapter テスト")
    print("=" * 70)
    
    adapter = FashnVideoAdapter(TEST_API_KEY)
    
    # テスト画像を作成
    test_image_path = Path("verification/virtual_tryon_result_1.png")
    
    if not test_image_path.exists():
        print(f"\n[ERROR] テスト画像が見つかりません: {test_image_path}")
        print("  verification/virtual_tryon_result_1.png を用意してください")
        sys.exit(1)
    
    # 画像を読み込み
    test_image = Image.open(test_image_path)
    
    print(f"\n[TEST] 入力画像: {test_image_path}")
    print(f"  サイズ: {test_image.size}")
    
    try:
        # 動画を生成
        video_url, metadata = adapter.generate_video(
            image=test_image,
            duration=5,  # 5秒（テスト用に短め）
            resolution="720p",  # 720p（テスト用）
            prompt="fashion model rotating and striking poses"
        )
        
        print(f"\n[SUCCESS] 動画URL取得: {video_url}")
        print(f"[SUCCESS] メタデータ: {metadata}")
        
        # 動画をダウンロード
        output_path = "verification/fashn_test_output.mp4"
        success = adapter.download_video(video_url, output_path)
        
        if success:
            print(f"\n[SUCCESS] テスト完了！")
            print(f"  出力: {output_path}")
        else:
            print("\n[FAILED] ダウンロード失敗")
    
    except Exception as e:
        print(f"\n[ERROR] テストエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


