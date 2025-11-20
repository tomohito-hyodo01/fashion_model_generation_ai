# Gemini 2.0 Flash Image Generation 移行ガイド

このドキュメントは、`fashion_model_generation_ai`プロジェクトで使用していた**Vertex AI経由のImagen 4**を、**google-generativeaiライブラリ経由のGemini 2.0 Flash Image Generation**に移行した手順と使用方法をまとめたものです。

## 📋 変更概要

### 以前の実装（Vertex AI）
- パッケージ: `google-cloud-aiplatform` + REST API
- 認証: サービスアカウントまたはGCPプロジェクトID
- 複雑な設定が必要

### 新しい実装（Gemini API）
- パッケージ: `google-generativeai` + `google-genai`
- 認証: **APIキーのみ**（簡単！）
- シンプルで使いやすい

## 🎯 実装内容

### 1. 新しいアダプター作成

**ファイル**: `app/core/adapters/gemini_imagen_adapter.py`

```python
class GeminiImagenAdapter(ProviderBase):
    """Google Generative AI (google-generativeai) Imagen 4 アダプタ"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        genai.configure(api_key=api_key)
        self.model_name = "imagen-4.0-generate-001"
```

### 2. メインウィンドウの更新

**ファイル**: `app/ui/main_window.py`

- 新しいプロバイダ「**Gemini Imagen 4 ⭐NEW: google-generativeai**」を追加
- `_create_adapter`メソッドで新しいアダプターをサポート
- デフォルトプロバイダとして設定

### 3. 設定ファイルの更新

**ファイル**: `app/models/generation_config.py`

```python
valid_providers = ["openai", "stability", "vertex", "gemini"]  # "gemini"を追加
```

**ファイル**: `requirements.txt`

```txt
google-generativeai>=0.8.0
google-genai>=0.2.0
```

## 🚀 使用方法

### 1. APIキーの設定

アプリケーションを起動し、「設定」→「APIキー設定」から：

1. プロバイダ: `gemini`
2. APIキー: `AIzaSyDLQVe0L5jn6R7lJNV4coe5FY-ICRHtSIg`

### 2. プロバイダの選択

メインウィンドウの「AI」ドロップダウンから：
- **Gemini Imagen 4 ⭐NEW: google-generativeai** を選択

### 3. 画像生成

通常通り、衣類画像を追加してモデル属性を設定し、「生成開始」をクリックします。

## 📊 プロバイダ比較

| 特徴 | Vertex AI (旧) | Gemini API (新) |
|------|---------------|-----------------|
| 認証 | サービスアカウント/プロジェクトID | APIキーのみ |
| 設定の簡単さ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| パッケージ | `google-cloud-aiplatform` | `google-generativeai` |
| 画質 | 同じ (Imagen 4.0) | 同じ (Imagen 4.0) |
| 価格 | $0.040/画像 | $0.040/画像 |
| 推奨度 | 企業向け | 個人・開発者向け |

## 🔧 技術詳細

### APIの呼び出し方法

```python
from google.genai import Client
from google.genai.types import GenerateImagesConfig

# クライアントの初期化
client = Client(api_key=API_KEY)

# 画像生成
response = client.models.generate_images(
    model="imagen-4.0-generate-001",
    prompt="A beautiful fashion model...",
    config=GenerateImagesConfig(
        number_of_images=1,
        aspect_ratio="1:1",
        safety_filter_level="block_low_and_above",
        person_generation="allow_adult",
    )
)

# 画像の取得
for generated_image in response.generated_images:
    image_bytes = generated_image.image.image_bytes
    pil_image = Image.open(BytesIO(image_bytes))
```

### サポートする設定

- **アスペクト比**: `1:1`, `9:16`, `16:9`
- **画像サイズ**: 1024x1024, 1024x1792, 1792x1024
- **出力枚数**: 1-4枚
- **セーフティフィルター**: `block_low_and_above`
- **人物生成**: `allow_adult`

## ✅ テスト結果

### テストプログラム

**ファイル**: `verification/test_gemini_imagen_adapter.py`

```bash
python verification\test_gemini_imagen_adapter.py
```

### 実行結果

```
============================================================
Gemini Imagen 4 Adapter テスト
============================================================
APIキー: AIzaSyDLQVe0L5jn6R7l...
------------------------------------------------------------
✓ API接続成功
✓ 画像生成成功！
生成枚数: 1
保存先: verification\test_gemini_imagen_1.png
============================================================

テスト結果: 成功 ✓
```

### 生成画像サンプル

- `verification/test_gemini_imagen_1.png`: エレガントな緑のジャケットとブラウンのパンツを着用したプロフェッショナルな女性ファッションモデル

## 📝 移行チェックリスト

- [x] 新しいアダプター作成 (`gemini_imagen_adapter.py`)
- [x] メインウィンドウの更新 (`main_window.py`)
- [x] 設定モデルの更新 (`generation_config.py`)
- [x] 依存パッケージの追加 (`requirements.txt`)
- [x] テストプログラムの作成と実行
- [x] 画像生成の動作確認

## 🎉 完了！

これで、`fashion_model_generation_ai`プロジェクトは、より簡単でシンプルな**Gemini API (google-generativeai)**を使用して**Imagen 4**で画像生成ができるようになりました！

## 📚 参考リンク

- [Google Generative AI Python SDK](https://github.com/google/generative-ai-python)
- [Imagen 4 Documentation](https://ai.google.dev/gemini-api/docs/imagen)
- [Google AI Studio](https://aistudio.google.com/)

---

**作成日**: 2025年11月10日  
**バージョン**: 1.0.0  
**対応モデル**: Imagen 4.0 (imagen-4.0-generate-001)

