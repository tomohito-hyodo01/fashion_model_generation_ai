"""
Gemini Imagen 4 Adapter テストプログラム

このプログラムは、新しく実装したGeminiImagenAdapterが
正しく動作するかをテストします。
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

# 出力画像ファイル名（プログラムと同じフォルダに保存）
output_dir = os.path.dirname(__file__) or "."


def test_gemini_imagen_adapter():
    """
    Gemini Imagen 4 Adapterをテストする
    """
    try:
        print("=" * 60)
        print("Gemini Imagen 4 Adapter テスト")
        print("=" * 60)
        print(f"APIキー: {API_KEY[:20]}...")
        print(f"出力ディレクトリ: {output_dir}")
        print("-" * 60)
        
        # アダプターの初期化
        print("アダプターを初期化しています...")
        adapter = GeminiImagenAdapter(api_key=API_KEY)
        print(f"使用モデル: {adapter.model_name}")
        
        # API接続確認
        print("API接続を確認しています...")
        if adapter.check_api_status():
            print("✓ API接続成功")
        else:
            print("✗ API接続失敗")
            return False
        
        # テスト用のモデル属性
        model_attrs = ModelAttributes(
            gender="female",
            age_range="20s",
            ethnicity="asian",
            body_type="standard",
            height="standard",
            pose="front",
            background="white",
        )
        
        # テスト用の生成設定
        config = GenerationConfig(
            provider="gemini",
            quality="standard",
            size="1024x1024",
            num_outputs=1,
        )
        
        # 画像生成テスト
        print("\n画像生成を開始しています...")
        print("プロンプト: 'A beautiful fashion model wearing elegant clothing'")
        
        # 簡易的な衣類アイテム（実際のファイルがない場合）
        garments = []
        
        # 画像生成
        images, metadata = adapter.generate(
            garments=garments,
            model_attrs=model_attrs,
            config=config,
            num_outputs=1
        )
        
        # 結果の確認
        if images and len(images) > 0:
            print("-" * 60)
            print("✓ 画像生成成功！")
            print(f"生成枚数: {len(images)}")
            print(f"メタデータ: {metadata}")
            
            # 画像を保存
            for i, image in enumerate(images):
                output_file = os.path.join(output_dir, f"test_gemini_imagen_{i+1}.png")
                image.save(output_file)
                print(f"保存先: {output_file}")
            
            print("=" * 60)
            return True
        else:
            print("-" * 60)
            print("✗ 画像が生成されませんでした")
            print(f"メタデータ: {metadata}")
            print("=" * 60)
            return False
        
    except Exception as e:
        print("-" * 60)
        print("✗ エラーが発生しました:")
        print(f"エラータイプ: {type(e).__name__}")
        print(f"エラー内容: {str(e)}")
        import traceback
        print("\nトレースバック:")
        traceback.print_exc()
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_gemini_imagen_adapter()
    
    if success:
        print("\nテスト結果: 成功 ✓")
        print("fashion_model_generation_aiプロジェクトで")
        print("Gemini Imagen 4 (google-generativeai)が使用できます！")
        exit(0)
    else:
        print("\nテスト結果: 失敗 ✗")
        exit(1)

