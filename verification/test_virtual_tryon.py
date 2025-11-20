"""
Virtual Try-On テストプログラム

このプログラムは、Gemini 2.5 Flash Imageを使って
服の画像から、その服を着たモデルを生成します。
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


def create_sample_garment_image():
    """
    サンプルの服の画像を作成（テスト用）
    実際のアプリでは、ユーザーがアップロードした画像を使用
    """
    # 600x800の緑色のTシャツ風の画像を作成
    img = Image.new('RGB', (600, 800), color=(34, 139, 34))  # Forest green
    
    draw = ImageDraw.Draw(img)
    
    # 襟を描画（白）
    draw.rectangle([(200, 50), (400, 100)], fill=(255, 255, 255))
    
    # 袖を描画
    draw.rectangle([(0, 100), (150, 400)], fill=(34, 139, 34))
    draw.rectangle([(450, 100), (600, 400)], fill=(34, 139, 34))
    
    # 本体
    draw.rectangle([(150, 100), (450, 600)], fill=(34, 139, 34))
    
    # テキストを追加
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    draw.text((150, 300), "Sample\nT-Shirt", fill=(255, 255, 255), font=font)
    
    sample_path = os.path.join(output_dir, "sample_tshirt.png")
    img.save(sample_path)
    print(f"Created sample garment image: {sample_path}")
    
    return sample_path


def test_virtual_tryon():
    """
    Virtual Try-Onをテストする
    """
    try:
        print("=" * 60)
        print("Virtual Try-On テスト - Gemini 2.5 Flash Image")
        print("=" * 60)
        print(f"APIキー: {API_KEY[:20]}...")
        print(f"出力ディレクトリ: {output_dir}")
        print("-" * 60)
        
        # サンプルの服の画像を作成
        print("\n1. サンプルの服の画像を作成...")
        garment_image_path = create_sample_garment_image()
        
        # アダプターの初期化
        print("\n2. Gemini 2.5 Flash Imageアダプターを初期化...")
        adapter = GeminiImagenAdapter(api_key=API_KEY)
        print(f"   使用モデル: {adapter.model_name}")
        
        # 衣類アイテムを作成
        print("\n3. 衣類アイテムを作成...")
        garment = ClothingItem(
            image_path=garment_image_path,
            clothing_type="TOP",
            colors=["#228B22"],  # Forest green
            pattern="solid",
            material="cotton",
            analyzed_description="A green t-shirt with white collar",
        )
        print(f"   衣類: {garment.display_name}")
        
        # モデル属性
        print("\n4. モデル属性を設定...")
        model_attrs = ModelAttributes(
            gender="female",
            age_range="20s",
            ethnicity="asian",
            body_type="standard",
            height="standard",
            pose="front",
            background="white",
        )
        print(f"   モデル: {model_attrs.gender}, {model_attrs.age_range}, {model_attrs.ethnicity}")
        
        # 生成設定
        print("\n5. 生成設定...")
        config = GenerationConfig(
            provider="gemini",
            quality="standard",
            size="1024x1024",
            num_outputs=1,
        )
        print(f"   出力枚数: {config.num_outputs}")
        
        # Virtual Try-On実行
        print("\n6. Virtual Try-On実行中...")
        print("   服の画像を入力として使用します...")
        images, metadata = adapter.generate(
            garments=[garment],
            model_attrs=model_attrs,
            config=config,
            num_outputs=1
        )
        
        # 結果の確認
        print("\n" + "=" * 60)
        if images and len(images) > 0:
            print("✓ Virtual Try-On 成功！")
            print(f"生成枚数: {len(images)}")
            print(f"メタデータ: {metadata}")
            
            # 画像を保存
            for i, image in enumerate(images):
                output_file = os.path.join(output_dir, f"virtual_tryon_result_{i+1}.png")
                image.save(output_file)
                print(f"保存先: {output_file}")
            
            print("=" * 60)
            print("\n✓ テスト成功！")
            print("生成された画像には、入力した服を着たモデルが表示されているはずです。")
            return True
        else:
            print("✗ 画像が生成されませんでした")
            print(f"メタデータ: {metadata}")
            print("=" * 60)
            
            if metadata.get("error"):
                print(f"\nエラー詳細: {metadata['error']}")
            
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
    success = test_virtual_tryon()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 Virtual Try-On機能が正常に動作しました！")
        print("=" * 60)
        print("\nこれで、fashion_model_generation_aiアプリで")
        print("服の画像をアップロードすると、その服を着たモデルが")
        print("生成されるようになります！")
        print("\n使い方:")
        print("1. アプリを起動")
        print("2. 服の画像をアップロード")
        print("3. AI選択で「Gemini 2.5 Flash Image」を選択")
        print("4. 「生成開始」をクリック")
        exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ テスト失敗")
        print("=" * 60)
        exit(1)

