"""
Gemini APIキー自動設定スクリプト

このスクリプトを実行すると、Gemini APIキーが自動的に保存されます。
"""

import sys
import os

# Windows環境でのUnicode出力を有効化
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# appディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from utils.api_key_manager import APIKeyManager

# APIキー
GEMINI_API_KEY = "AIzaSyDLQVe0L5jn6R7lJNV4coe5FY-ICRHtSIg"

def setup_gemini_api_key():
    """Gemini APIキーをセットアップ"""
    print("=" * 60)
    print("Gemini APIキー自動設定")
    print("=" * 60)
    
    # APIキーマネージャーを初期化
    print("\n1. APIキーマネージャーを初期化...")
    api_key_manager = APIKeyManager()
    
    # Gemini APIキーを保存
    print("2. Gemini APIキーを保存...")
    api_key_manager.save_api_key("gemini", GEMINI_API_KEY)
    
    # 確認
    print("3. 保存されたAPIキーを確認...")
    saved_key = api_key_manager.load_api_key("gemini")
    
    if saved_key:
        print(f"   [OK] APIキーが正常に保存されました")
        print(f"   APIキー: {saved_key[:20]}...")
        print("\n" + "=" * 60)
        print("セットアップ完了")
        print("=" * 60)
        print("\nアプリを起動してください:")
        print("  python app/main.py")
        print("\nまたは:")
        print("  run.ps1")
        return True
    else:
        print("   [ERROR] APIキーの保存に失敗しました")
        return False

if __name__ == "__main__":
    try:
        success = setup_gemini_api_key()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

