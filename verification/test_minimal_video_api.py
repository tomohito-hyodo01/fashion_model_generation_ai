"""
Stability AI Video API 最小テストコード

最小限のコードでAPIの動作を確認します。
"""

import os
import sys
import requests
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# テスト用APIキー
TEST_API_KEY = "sk-IiO8gDGVp0ioHnrZHctNMFlI5gGNouo72m548qgC11pOJPet"

def test_minimal():
    """最小限のテスト"""
    print("=" * 70)
    print("Stability AI Video API 最小テストコード")
    print("=" * 70)
    
    # 入力画像
    image_path = "verification/sample_tshirt.png"
    
    if not os.path.exists(image_path):
        print(f"\n[ERROR] 画像が見つかりません: {image_path}")
        return
    
    # テスト1: v2beta エンドポイント
    print("\n[TEST 1] v2beta エンドポイントをテスト")
    print(f"URL: https://api.stability.ai/v2beta/image-to-video")
    print(f"APIキー: {TEST_API_KEY[:20]}...")
    
    try:
        with open(image_path, "rb") as f:
            resp = requests.post(
                "https://api.stability.ai/v2beta/image-to-video",
                headers={
                    "authorization": TEST_API_KEY,
                    "accept": "application/json"
                },
                files={"image": f},
                data={
                    "seed": 0,
                    "cfg_scale": 2.5,
                    "motion_bucket_id": 40
                },
                timeout=30
            )
        
        print(f"\nステータスコード: {resp.status_code}")
        print(f"レスポンスヘッダー:")
        for key, value in resp.headers.items():
            print(f"  {key}: {value}")
        print(f"\nレスポンス本文:")
        print(resp.text[:500])  # 最初の500文字
        
        if resp.status_code == 200:
            print("\n[SUCCESS] リクエスト成功！")
            print(f"JSON: {resp.json()}")
        else:
            print(f"\n[FAILED] エラー: {resp.status_code}")
            
    except Exception as e:
        print(f"\n[ERROR] 例外発生: {e}")
        import traceback
        traceback.print_exc()
    
    # テスト2: APIキーの検証（エンジンリスト取得）
    print("\n" + "=" * 70)
    print("[TEST 2] APIキーの検証（エンジンリスト取得）")
    print("=" * 70)
    
    try:
        # Stability AIの他のエンドポイントでAPIキーを検証
        resp = requests.get(
            "https://api.stability.ai/v1/engines/list",
            headers={"authorization": TEST_API_KEY},
            timeout=10
        )
        
        print(f"\nステータスコード: {resp.status_code}")
        print(f"レスポンス: {resp.text[:500]}")
        
        if resp.status_code == 200:
            print("\n[SUCCESS] APIキーは有効です！")
            engines = resp.json()
            print(f"利用可能なエンジン数: {len(engines)}")
        else:
            print(f"\n[FAILED] APIキー検証失敗: {resp.status_code}")
            
    except Exception as e:
        print(f"\n[ERROR] 例外発生: {e}")
        import traceback
        traceback.print_exc()
    
    # テスト3: アカウント情報の取得
    print("\n" + "=" * 70)
    print("[TEST 3] アカウント情報の取得")
    print("=" * 70)
    
    try:
        resp = requests.get(
            "https://api.stability.ai/v1/user/account",
            headers={"authorization": TEST_API_KEY},
            timeout=10
        )
        
        print(f"\nステータスコード: {resp.status_code}")
        print(f"レスポンス: {resp.text}")
        
        if resp.status_code == 200:
            account = resp.json()
            print("\n[SUCCESS] アカウント情報:")
            print(f"  Email: {account.get('email', 'N/A')}")
            print(f"  Organization: {account.get('organizations', [])}")
            print(f"  Profile Picture: {account.get('profile_picture', 'N/A')}")
        else:
            print(f"\n[INFO] アカウント情報取得失敗: {resp.status_code}")
            
    except Exception as e:
        print(f"\n[ERROR] 例外発生: {e}")
    
    # テスト4: 別のv2betaエンドポイント（stable-image）
    print("\n" + "=" * 70)
    print("[TEST 4] v2beta/stable-image エンドポイントの確認")
    print("=" * 70)
    
    try:
        # stable-imageの存在確認
        resp = requests.options(
            "https://api.stability.ai/v2beta/stable-image/generate/ultra",
            headers={"authorization": TEST_API_KEY},
            timeout=10
        )
        
        print(f"\nステータスコード: {resp.status_code}")
        print(f"Allow: {resp.headers.get('Allow', 'N/A')}")
        
        if resp.status_code in [200, 405]:  # OPTIONS may return 405
            print("\n[INFO] v2beta エンドポイントは存在します")
        else:
            print(f"\n[INFO] ステータス: {resp.status_code}")
            
    except Exception as e:
        print(f"\n[ERROR] 例外発生: {e}")
    
    print("\n" + "=" * 70)
    print("テスト完了")
    print("=" * 70)


if __name__ == "__main__":
    test_minimal()


