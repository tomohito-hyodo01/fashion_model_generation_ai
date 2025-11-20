# Vertex AI 画像生成モデル テストプログラム

## 概要

このフォルダには、Google Vertex AI APIの接続と画像生成機能をテストするプログラムが含まれています。

## ファイル

- `test_imagen.py`: Imagen 4.0 モデルテストプログラム
- `test_gemini_flash_image.py`: Gemini 2.5 Flash Image モデルテストプログラム

## 使用方法

### 1. 前提条件

Google Cloud Platform (GCP)の認証情報が設定されている必要があります。

#### 認証方法

以下のいずれかの方法で認証を設定してください：

**方法1: Application Default Credentials (ADC) を使用**

```powershell
gcloud auth application-default login
```

**方法2: サービスアカウントキーを使用**

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="path\to\your\service-account-key.json"
```

### 2. 必要なパッケージのインストール

プロジェクトのルートディレクトリで仮想環境が有効化されていることを確認してください：

```powershell
# 仮想環境の有効化（まだの場合）
.\venv\Scripts\Activate.ps1

# Google Gen AIライブラリのインストール（まだの場合）
pip install google-genai
```

### 3. テストプログラムの実行

#### Imagen 4.0 モデルのテスト

```powershell
# verificationディレクトリに移動
cd verification

# Imagenテストプログラムを実行
python test_imagen.py
```

#### Gemini 2.5 Flash Image モデルのテスト

```powershell
# verificationディレクトリに移動
cd verification

# Gemini Flash Imageテストプログラムを実行
python test_gemini_flash_image.py
```

### 4. 実行結果

#### Imagen 4.0 モデル

成功すると、以下のような出力が表示され、`output-image.png`が生成されます：

```
============================================================
Google Imagen (Vertex AI) 画像生成テスト
============================================================
プロジェクトID: gen-lang-client-0033034512
ロケーション: us-central1
出力ファイル: C:\InProc\fashion_model_generation_ai\verification\output-image.png
------------------------------------------------------------
クライアントを初期化しています...
画像生成を開始しています...
プロンプト: 'A dog reading a newspaper'
画像を保存しています...
------------------------------------------------------------
✓ 画像生成成功！
ファイルサイズ: 1,234,567 バイト
保存先: C:\InProc\fashion_model_generation_ai\verification\output-image.png
============================================================

テスト結果: 成功 ✓
```

#### Gemini 2.5 Flash Image モデル

成功すると、以下のような出力が表示され、`output-gemini-flash.png`が生成されます：

```
============================================================
Gemini 2.5 Flash Image モデルテスト
============================================================
プロジェクトID: gen-lang-client-0033034512
ロケーション: us-central1
モデル: gemini-2.5-flash-image
出力ファイル: C:\InProc\fashion_model_generation_ai\verification\output-gemini-flash.png
------------------------------------------------------------
クライアントを初期化しています...
画像生成を開始しています...
プロンプト: 'A beautiful sunset over Mount Fuji with cherry blossoms in the foreground'
画像を保存しています...
------------------------------------------------------------
✓ 画像生成成功！
ファイルサイズ: 1,234,567 バイト
保存先: C:\InProc\fashion_model_generation_ai\verification\output-gemini-flash.png
============================================================

テスト結果: 成功 ✓
```

## プロジェクト情報

- **プロジェクトID**: `gen-lang-client-0033034512`
- **ロケーション**: `us-central1`

### モデル別設定

#### Imagen 4.0
- **モデル名**: `imagen-4.0-generate-001`
- **画像サイズ**: `2K`
- **出力ファイル**: `output-image.png`
- **テストプロンプト**: "A dog reading a newspaper"

#### Gemini 2.5 Flash Image
- **モデル名**: `gemini-2.5-flash-image`
- **画像数**: `1`
- **出力ファイル**: `output-gemini-flash.png`
- **テストプロンプト**: "A beautiful sunset over Mount Fuji with cherry blossoms in the foreground"

## トラブルシューティング

### 認証エラーが発生する場合

1. GCPプロジェクトで Vertex AI API が有効化されているか確認
2. 認証情報が正しく設定されているか確認
3. 適切な権限（Vertex AI User等）があるか確認

### インポートエラーが発生する場合

```powershell
pip install --upgrade google-genai
```

## 注意事項

- このテストプログラムは画像生成APIを実際に呼び出すため、課金が発生します
- 生成される画像ファイル：
  - Imagen 4.0: `output-image.png`
  - Gemini 2.5 Flash Image: `output-gemini-flash.png`
- 両方のテストプログラムを独立して実行できます
- 各モデルで異なるAPIエンドポイントを使用します

---

## ❌ Stability AI Video Generation テスト（結果：利用不可）

### テスト結果

**⚠️ 重要**: Stable Video Diffusion APIは**現在利用できません**。

```
エラー: 404 Not Found
エンドポイント: https://api.stability.ai/v2alpha/generation/image-to-video
```

### 原因分析

1. **エンドポイントが存在しない**: v2alphaエンドポイントは公開されていない
2. **公式ドキュメントに未掲載**: API Referenceに記載がない
3. **ベータ限定アクセス**: 限られたユーザーのみがアクセス可能な可能性

### テストコード

参考のため、テストコードは残してあります：

```bash
# テスト実行（404エラーになります）
python verification/test_stability_video.py
```

### APIキーの設定

以下のいずれかの方法でAPIキーを設定してください：

1. **環境変数**（推奨）:
   ```bash
   # Windows (PowerShell)
   $env:STABILITY_API_KEY = "your_api_key_here"
   
   # Windows (コマンドプロンプト)
   set STABILITY_API_KEY=your_api_key_here
   ```

2. **アプリケーションの設定画面**:
   - メインアプリを起動
   - 設定 → APIキー設定 → Stability AI
   - APIキーを入力して保存

### パラメータ

プログラム内で以下のパラメータを調整できます：

- `cfg_scale`: 原画像への忠実度（1.0-10.0、デフォルト: 2.5）
- `motion_bucket_id`: 動きの大きさ（1-255、デフォルト: 40）
  - 小さい値: 静かな動き
  - 大きい値: ダイナミックな動き

### 出力

- **保存先**: `verification/output_video.mp4`
- **形式**: MP4動画（約2秒）
- **生成時間**: 約30-60秒

### 注意事項（Video API）

- ⚠️ **アルファ版API**: `v2alpha` エンドポイントを使用しているため、仕様が変更される可能性があります
- 💰 **コスト**: 1動画あたり約20クレジット（約$0.20）
- ⏱️ **処理時間**: 平均40秒程度かかります
- 📏 **制限**: 短尺動画（約2秒）のみ生成可能

### 動画生成の代替案（実装可能）

Stable Video APIが使えない場合、以下の代替案があります：

#### ✅ **方法1: 画像シーケンスから疑似動画を生成**（推奨）

複数の角度・ポーズの画像を連続生成して、MP4動画を作成します。

```bash
# 必要なパッケージをインストール
pip install opencv-python

# 画像シーケンスから動画を生成
python verification/test_image_sequence_video.py
```

**特徴:**
- ✅ 完全に実装可能（追加API不要）
- ✅ 複数角度の画像を自動生成
- ✅ カスタマイズ可能（FPS、duration等）
- ⚠️ 滑らかな動きではなくスライドショー形式

**生成される動画:**
- `verification/output_sequence_video.mp4`
- `verification/rotation_demo.mp4`（回転デモ）

#### 方法2: Stability AIサポートに問い合わせ

ベータアクセスをリクエストすることも可能です：

**問い合わせ先**: https://stability.ai/contact

```
件名: Stable Video Diffusion API Access Request

本文:
I would like to access the Stable Video Diffusion API 
(v2alpha/generation/image-to-video) for my fashion model 
generation application. Could you provide information on 
how to get access?
```

#### 方法3: 他のVideo Generation API

- **Runway Gen-3**: 商用利用可能（別途契約必要）
- **Pika Labs**: テキスト→動画生成
- **将来的にGoogle Veo**: 現在は未公開

---

## 追加トラブルシューティング

### Stability Video API エラー: "403 Forbidden"
- APIキーにVideo API へのアクセス権限がない可能性があります
- Stability AIサポートに連絡してベータアクセスをリクエストしてください

### Stability Video API エラー: "404 Not Found"
- v2alpha エンドポイントが利用できない可能性があります
- 最新のAPIドキュメントを確認してください: https://platform.stability.ai/docs/api-reference

