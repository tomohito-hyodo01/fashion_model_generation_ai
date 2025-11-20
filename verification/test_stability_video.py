"""
Stability AI Stable Video Diffusion API のテストコード

画像から動画（MP4）を生成して保存します。

使用方法:
    python verification/test_stability_video.py

必要な環境変数:
    STABILITY_API_KEY: Stability AI APIキー（または app/utils/api_key_manager.py から読み込み）
"""

import os
import sys
import time
import base64
import requests
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def get_api_key() -> str:
    """APIキーを取得"""
    # テスト用: 直接APIキーを指定
    TEST_API_KEY = "sk-IiO8gDGVp0ioHnrZHctNMFlI5gGNouo72m548qgC11pOJPet"
    
    if TEST_API_KEY:
        print("[OK] テスト用APIキーを使用します")
        return TEST_API_KEY
    
    # 1. 環境変数から取得
    api_key = os.environ.get("STABILITY_API_KEY")
    
    if not api_key:
        # 2. APIKeyManagerから取得を試みる
        try:
            from app.utils.api_key_manager import APIKeyManager
            manager = APIKeyManager()
            api_key = manager.load_api_key("stability")
            if api_key:
                print("[OK] APIキーをAPIKeyManagerから読み込みました")
        except Exception as e:
            print(f"[WARN] APIKeyManagerからの読み込みに失敗: {e}")
    else:
        print("[OK] APIキーを環境変数から読み込みました")
    
    if not api_key:
        raise RuntimeError(
            "STABILITY_API_KEY が未設定です。\n"
            "以下のいずれかの方法で設定してください：\n"
            "1. 環境変数: set STABILITY_API_KEY=your_key\n"
            "2. アプリの設定画面からStability AI APIキーを登録"
        )
    
    return api_key


def start_image_to_video(
    api_key: str,
    image_path: str,
    seed: int = 0,
    cfg_scale: float = 2.5,
    motion_bucket_id: int = 40
) -> str:
    """
    画像から動画生成ジョブを開始して、ジョブIDを返す
    
    Args:
        api_key: Stability AI APIキー
        image_path: 入力画像のパス
        seed: シード値（0=ランダム）
        cfg_scale: 原画像への忠実度（1.0-10.0）
        motion_bucket_id: 動きの大きさ（1-255、小さいほど静か）
    
    Returns:
        生成ジョブのID
    """
    API_HOST = "https://api.stability.ai"
    # v2beta エンドポイントに変更（最新版）
    url = f"{API_HOST}/v2beta/image-to-video"
    
    print(f"\n[送信] 動画生成リクエストを送信中...")
    print(f"   入力画像: {image_path}")
    print(f"   cfg_scale: {cfg_scale}")
    print(f"   motion_bucket_id: {motion_bucket_id}")
    print(f"   エンドポイント: {url}")
    
    # ファイルを開く
    with open(image_path, "rb") as img_file:
        files = {
            "image": img_file,
        }
        data = {
            "seed": seed,
            "cfg_scale": cfg_scale,
            "motion_bucket_id": motion_bucket_id
        }
        headers = {
            # Bearer なしで API キーそのものを渡す（v2beta の仕様）
            "authorization": api_key,
            "accept": "application/json",
        }
        
        try:
            resp = requests.post(url, headers=headers, files=files, data=data, timeout=30)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"\n[ERROR] APIエラー: {e}")
            print(f"   レスポンス: {resp.text}")
            raise
        except Exception as e:
            print(f"\n[ERROR] リクエストエラー: {e}")
            raise
    
    result = resp.json()
    vid_id = result.get("id")
    
    if not vid_id:
        raise RuntimeError(f"レスポンスにIDが含まれていません: {result}")
    
    print(f"[OK] 生成ジョブID: {vid_id}")
    return vid_id


def wait_and_download_video(
    api_key: str,
    vid_id: str,
    out_path: str,
    max_wait_time: int = 300
) -> bool:
    """
    ジョブが完了するまでポーリングして、完了したら MP4 を保存
    
    Args:
        api_key: Stability AI APIキー
        vid_id: 生成ジョブのID
        out_path: 出力動画のパス
        max_wait_time: 最大待機時間（秒）
    
    Returns:
        成功した場合はTrue
    """
    API_HOST = "https://api.stability.ai"
    # v2beta エンドポイントに変更（最新版）
    url = f"{API_HOST}/v2beta/image-to-video/result/{vid_id}"
    
    headers = {
        # Bearer なしで API キーそのものを渡す（v2beta の仕様）
        "authorization": api_key,
        "accept": "application/json",  # base64エンコードされた動画を取得
    }
    
    print(f"\n[待機] 動画生成を待機中...")
    start_time = time.time()
    poll_count = 0
    
    while True:
        elapsed_time = time.time() - start_time
        
        # タイムアウトチェック
        if elapsed_time > max_wait_time:
            print(f"\n[ERROR] タイムアウト: {max_wait_time}秒を超えました")
            return False
        
        poll_count += 1
        print(f"   ポーリング #{poll_count} ({int(elapsed_time)}秒経過)...")
        
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            
            # 202 = まだ生成中
            if resp.status_code == 202:
                print(f"   ステータス: 202 (処理中) - 10秒後に再試行")
                time.sleep(10)
                continue
            
            # その他のエラー
            if resp.status_code != 200:
                print(f"\n[WARN] ステータスコード: {resp.status_code}")
                print(f"   レスポンス: {resp.text}")
                time.sleep(10)
                continue
            
            # 成功
            data = resp.json()
            
            # videoフィールドが存在するか確認
            if "video" not in data:
                print(f"   [WARN] videoフィールドが見つかりません - 10秒後に再試行")
                print(f"   レスポンス: {data}")
                time.sleep(10)
                continue
            
            # base64デコードして保存
            video_b64 = data["video"]
            video_binary = base64.b64decode(video_b64)
            
            # 出力ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
            with open(out_path, "wb") as f:
                f.write(video_binary)
            
            file_size_mb = len(video_binary) / (1024 * 1024)
            print(f"\n[OK] 動画を保存しました: {out_path}")
            print(f"   ファイルサイズ: {file_size_mb:.2f} MB")
            print(f"   生成時間: {int(elapsed_time)}秒")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"   [WARN] リクエストエラー: {e} - 10秒後に再試行")
            time.sleep(10)
            continue
        except Exception as e:
            print(f"\n[ERROR] 予期しないエラー: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_image_to_video(
    input_image: str = "verification/sample_tshirt.png",
    output_video: str = "verification/output_video.mp4",
    cfg_scale: float = 2.5,
    motion_bucket_id: int = 40
):
    """
    画像から動画を生成するテスト
    
    Args:
        input_image: 入力画像のパス
        output_video: 出力動画のパス
        cfg_scale: 原画像への忠実度
        motion_bucket_id: 動きの大きさ
    """
    print("=" * 70)
    print("Stability AI Stable Video Diffusion API テスト")
    print("=" * 70)
    
    # 入力画像の存在確認
    if not os.path.exists(input_image):
        print(f"\n[ERROR] エラー: 入力画像が見つかりません: {input_image}")
        print(f"   利用可能な画像を指定してください。")
        return False
    
    try:
        # APIキーを取得
        api_key = get_api_key()
        
        # 動画生成開始
        generation_id = start_image_to_video(
            api_key=api_key,
            image_path=input_image,
            cfg_scale=cfg_scale,
            motion_bucket_id=motion_bucket_id
        )
        
        # 完了を待って動画をダウンロード
        success = wait_and_download_video(
            api_key=api_key,
            vid_id=generation_id,
            out_path=output_video,
            max_wait_time=300  # 最大5分
        )
        
        if success:
            print("\n" + "=" * 70)
            print("[SUCCESS] テスト成功！")
            print(f"   出力動画: {output_video}")
            print("=" * 70)
            return True
        else:
            print("\n" + "=" * 70)
            print("[FAILED] テスト失敗")
            print("=" * 70)
            return False
            
    except Exception as e:
        print(f"\n[ERROR] エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # デフォルトではsample_tshirt.pngを使用
    # コマンドライン引数で画像を指定することも可能
    if len(sys.argv) > 1:
        input_image = sys.argv[1]
    else:
        input_image = "verification/sample_tshirt.png"
    
    # 出力動画のパス
    output_video = "verification/output_video.mp4"
    
    # テスト実行
    success = test_image_to_video(
        input_image=input_image,
        output_video=output_video,
        cfg_scale=2.5,      # 原画像への忠実度
        motion_bucket_id=40  # 動きの大きさ（小さい値 = 静かな動き）
    )
    
    sys.exit(0 if success else 1)

