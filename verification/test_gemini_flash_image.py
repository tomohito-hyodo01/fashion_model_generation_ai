"""
Gemini 2.5 Flash Image モデルテストプログラム

このプログラムは、APIキーを使用してGemini 2.5 Flash Imageモデルで
画像生成をテストします。
"""

import os
import sys
import google.generativeai as genai
from PIL import Image
import io

# Windows環境でのUnicode出力を有効化
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# APIキー
API_KEY = "AIzaSyDLQVe0L5jn6R7lJNV4coe5FY-ICRHtSIg"

# 出力画像ファイル名（プログラムと同じフォルダに保存）
output_file = os.path.join(os.path.dirname(__file__) or ".", "output-gemini-image.png")

def test_gemini_flash_generation():
    """
    Gemini 2.5 Flash Imageを使用して画像生成をテストする
    """
    try:
        print("=" * 60)
        print("Gemini 2.5 Flash Image モデルテスト")
        print("=" * 60)
        print(f"APIキー: {API_KEY[:20]}...")
        print(f"モデル: gemini-2.5-flash-image")
        print(f"出力ファイル: {output_file}")
        print("-" * 60)
        
        # APIキーの設定
        print("APIを設定しています...")
        genai.configure(api_key=API_KEY)
        
        # モデルの初期化
        print("モデルを初期化しています...")
        model = genai.GenerativeModel(model_name="gemini-2.5-flash-image")
        
        # 画像生成のリクエスト
        print("画像生成を開始しています...")
        test_prompt = "富士山と桜の美しい風景の写真を生成してください。夕焼けの背景で、デジタルアートスタイルで。"
        print(f"プロンプト: '{test_prompt}'")
        
        response = model.generate_content([test_prompt])
        
        # 生成された画像を保存
        print("レスポンスを処理しています...")
        
        # レスポンスの内容を確認してデバッグ
        print(f"レスポンスタイプ: {type(response)}")
        print(f"レスポンス属性: {dir(response)}")
        
        # candidatesを確認
        if hasattr(response, 'candidates'):
            print(f"Candidates数: {len(response.candidates)}")
            for c_idx, candidate in enumerate(response.candidates):
                print(f"Candidate {c_idx} content: {candidate.content}")
                if hasattr(candidate.content, 'parts'):
                    for p_idx, part in enumerate(candidate.content.parts):
                        print(f"  Part {p_idx}: {part}")
                        
                        # inline_dataを確認
                        if hasattr(part, 'inline_data') and part.inline_data:
                            inline_data = part.inline_data
                            print(f"    inline_data found!")
                            print(f"    mime_type: {inline_data.mime_type}")
                            print(f"    data length: {len(inline_data.data) if inline_data.data else 0}")
                            
                            if inline_data.data:
                                # バイナリデータとして直接保存
                                with open(output_file, 'wb') as f:
                                    f.write(inline_data.data)
                                
                                bytes_count = len(inline_data.data)
                                print("-" * 60)
                                print("✓ 画像生成成功！")
                                print(f"ファイルサイズ: {bytes_count:,} バイト")
                                print(f"保存先: {output_file}")
                                print("=" * 60)
                                return True
                        
                        # textを確認
                        if hasattr(part, 'text') and part.text:
                            print(f"    text: {part.text}")
        
        print("-" * 60)
        print("✗ 画像が生成されませんでした")
        print("=" * 60)
        return False
        
    except Exception as e:
        print("-" * 60)
        print("✗ エラーが発生しました:")
        print(f"エラータイプ: {type(e).__name__}")
        print(f"エラー内容: {str(e)}")
        print("-" * 60)
        print("ヒント:")
        print("- APIキーが正しく設定されているか確認してください")
        print("- モデル名が正しいか確認してください")
        print("- 画像生成にはクォータ制限や請求設定が必要な場合があります")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = test_gemini_flash_generation()
    
    if success:
        print("\nテスト結果: 成功 ✓")
        exit(0)
    else:
        print("\nテスト結果: 失敗 ✗")
        exit(1)

