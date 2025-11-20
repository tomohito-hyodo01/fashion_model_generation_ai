"""
座位ポーズのテストプログラム
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
from PIL import Image, ImageDraw, ImageFont

# Windows環境でのUnicode出力を有効化
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# APIキー
API_KEY = "AIzaSyDLQVe0L5jn6R7lJNV4coe5FY-ICRHtSIg"

# 出力ディレクトリ
output_dir = os.path.dirname(__file__) or "."


def test_sitting_pose():
    """座位ポーズのテスト"""
    try:
        print("=" * 60)
        print("座位ポーズテスト - Gemini 2.5 Flash Image")
        print("=" * 60)
        
        # サンプルの服の画像（既存のものを使用）
        garment_image_path = os.path.join(output_dir, "sample_tshirt.png")
        
        if not os.path.exists(garment_image_path):
            print("sample_tshirt.pngが見つかりません。先にtest_virtual_tryon.pyを実行してください。")
            return False
        
        # アダプターの初期化
        print("\nGemini 2.5 Flash Imageアダプターを初期化...")
        adapter = GeminiImagenAdapter(api_key=API_KEY)
        
        # 衣類アイテムを作成
        garment = ClothingItem(
            image_path=garment_image_path,
            clothing_type="TOP",
            colors=["#228B22"],
            pattern="solid",
            material="cotton",
            analyzed_description="A green t-shirt with white text",
        )
        
        # モデル属性（座位を指定）
        print("\nモデル属性を設定...")
        model_attrs = ModelAttributes(
            gender="female",
            age_range="20s",
            ethnicity="european",  # ヨーロッパ系でテスト
            body_type="standard",
            height="standard",
            pose="sitting",  # 座位を指定
            background="studio",  # スタジオ背景を指定
        )
        print(f"  地域: {model_attrs.ethnicity} (ヨーロッパ)")
        print(f"  ポーズ: {model_attrs.pose} (座位)")
        print(f"  背景: {model_attrs.background} (スタジオ)")
        
        # 生成設定
        config = GenerationConfig(
            provider="gemini",
            quality="standard",
            size="1024x1024",
            num_outputs=1,
        )
        
        # Virtual Try-On実行
        print("\n画像生成中...")
        images, metadata = adapter.generate(
            garments=[garment],
            model_attrs=model_attrs,
            config=config,
            num_outputs=1
        )
        
        # 結果の確認
        print("\n" + "=" * 60)
        if images and len(images) > 0:
            print("[OK] 画像生成成功")
            
            # 画像を保存
            output_file = os.path.join(output_dir, "test_sitting_pose.png")
            images[0].save(output_file)
            print(f"保存先: {output_file}")
            print("\n確認事項:")
            print("  - モデルは座っていますか？")
            print("  - 背景はスタジオ風ですか？")
            print("  - Tシャツの色とテキストは正確ですか？")
            print("=" * 60)
            return True
        else:
            print("[ERROR] 画像が生成されませんでした")
            print(f"メタデータ: {metadata}")
            return False
        
    except Exception as e:
        print(f"\n[ERROR] エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_sitting_pose()
    sys.exit(0 if success else 1)

