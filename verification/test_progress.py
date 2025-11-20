"""
進捗表示テストプログラム
"""

import os
import sys

# プロジェクトのルートディレクトリとappディレクトリをパスに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app_dir = os.path.join(project_root, 'app')
sys.path.insert(0, project_root)
sys.path.insert(0, app_dir)

from core.adapters.gemini_imagen_adapter import GeminiImagenAdapter
from models.clothing_item import ClothingItem
from models.model_attributes import ModelAttributes
from models.generation_config import GenerationConfig

# Windows環境でのUnicode出力を有効化
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# APIキー
API_KEY = "AIzaSyDLQVe0L5jn6R7lJNV4coe5FY-ICRHtSIg"

# 出力ディレクトリ
output_dir = os.path.dirname(__file__) or "."


def test_progress():
    """進捗表示のテスト"""
    try:
        print("=" * 60)
        print("進捗表示テスト")
        print("=" * 60)
        
        # サンプルの服の画像
        garment_image_path = os.path.join(output_dir, "sample_tshirt.png")
        
        if not os.path.exists(garment_image_path):
            print("sample_tshirt.pngが見つかりません。")
            return False
        
        # 進捗を表示するコールバック
        def progress_callback(step: str, percentage: int):
            """進捗を表示"""
            bar_length = 40
            filled = int(bar_length * percentage / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r[{bar}] {percentage}% - {step}", end='', flush=True)
        
        # アダプターの初期化
        print("\nアダプターを初期化...\n")
        adapter = GeminiImagenAdapter(api_key=API_KEY)
        adapter.set_progress_callback(progress_callback)
        
        # 衣類アイテムを作成
        garment = ClothingItem(
            image_path=garment_image_path,
            clothing_type="TOP",
            colors=["#228B22"],
            pattern="solid",
            material="cotton",
            analyzed_description="A green t-shirt",
        )
        
        # モデル属性
        model_attrs = ModelAttributes(
            gender="female",
            age_range="20s",
            ethnicity="asian",
            body_type="standard",
            height="standard",
            pose="front",
            background="white",
        )
        
        # 生成設定
        config = GenerationConfig(
            provider="gemini",
            quality="standard",
            size="1024x1024",
            num_outputs=1,
        )
        
        # 画像生成
        print("画像生成開始...\n")
        images, metadata = adapter.generate(
            garments=[garment],
            model_attrs=model_attrs,
            config=config,
            num_outputs=1
        )
        
        print("\n\n" + "=" * 60)
        if images and len(images) > 0:
            print("[OK] 画像生成成功")
            
            # 画像を保存
            output_file = os.path.join(output_dir, "test_progress_result.png")
            images[0].save(output_file)
            print(f"保存先: {output_file}")
            print("=" * 60)
            print("\n進捗表示が実際の処理に応じて更新されましたか？")
            return True
        else:
            print("[ERROR] 画像が生成されませんでした")
            return False
        
    except Exception as e:
        print(f"\n[ERROR] エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_progress()
    sys.exit(0 if success else 1)

