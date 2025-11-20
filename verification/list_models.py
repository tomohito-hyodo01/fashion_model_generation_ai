"""
Google Gen AI 利用可能モデルリスト取得プログラム

このプログラムは、APIキーで利用可能なモデルの一覧を表示します。
"""

import sys
from google import genai

# Windows環境でのUnicode出力を有効化
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# APIキー
API_KEY = "AIzaSyDLQVe0L5jn6R7lJNV4coe5FY-ICRHtSIg"

def list_available_models():
    """
    利用可能なモデルをリストアップする
    """
    try:
        print("=" * 60)
        print("Google Gen AI 利用可能モデル一覧")
        print("=" * 60)
        print(f"APIキー: {API_KEY[:20]}...")
        print("-" * 60)
        
        # Google Gen AI クライアントの初期化
        print("クライアントを初期化しています...")
        client = genai.Client(api_key=API_KEY)
        
        # モデルのリストを取得
        print("モデル一覧を取得しています...")
        models = client.models.list()
        
        print("\n利用可能なモデル:")
        print("-" * 60)
        
        for model in models:
            print(f"\nモデル名: {model.name}")
            if hasattr(model, 'display_name'):
                print(f"  表示名: {model.display_name}")
            if hasattr(model, 'description'):
                print(f"  説明: {model.description}")
            if hasattr(model, 'supported_generation_methods'):
                print(f"  対応メソッド: {model.supported_generation_methods}")
        
        print("\n" + "=" * 60)
        return True
        
    except Exception as e:
        print("-" * 60)
        print("✗ エラーが発生しました:")
        print(f"エラータイプ: {type(e).__name__}")
        print(f"エラー内容: {str(e)}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = list_available_models()
    
    if success:
        print("\nモデル一覧取得: 成功 ✓")
        exit(0)
    else:
        print("\nモデル一覧取得: 失敗 ✗")
        exit(1)

