# Virtual Fashion Try-On v2.1

衣類画像をファッションモデルに忠実に着せた画像と動画を生成するWindowsデスクトップアプリケーション

## ✨ v2.1の新機能（Phase 4）

- 🎬 **FASHN AI動画生成**: 画像から高品質な動画を生成
- 🎭 **実際の動き**: モデルが回転・歩行・ポーズ変化
- ⚙️ **柔軟な設定**: 長さ（5/10秒）、解像度（480p/720p/1080p）
- 📝 **カスタムプロンプト**: 動きを自由に指示可能

## ✨ v2.0の機能

- 🎨 **ポーズ画像ギャラリー**: 画像で直感的にポーズを選択
- 🖼️ **背景画像ギャラリー**: 画像で背景を選択
- 📷 **マルチアングル生成**: 同じ衣類を複数角度から撮影
- 💬 **チャット修正機能**: 対話形式で画像を修正
- 🤖 **AI自然言語理解**: 「もっと明るく」等の指示を自動解析
- 📸 **カスタムポーズ**: 画像をアップロードしてポーズを自動認識（MediaPipe）
- 💾 **履歴管理**: 生成結果を永続化
- 📁 **プロジェクト管理**: セッション単位で整理

## 特徴

- ⭐ **画像参照機能**: Gemini 2.5 Flash Imageで衣類画像を直接参照して忠実に再現
- **衣類の忠実再現**: image-to-image技術により、元の衣類を高精度で再現
- **複数AIプロバイダ対応**: OpenAI (DALL-E 3)、Stability AI SD 3.5、Google Imagen 4から選択可能
- **柔軟な出力**: 1〜4枚の画像を同時生成（種類違い or 角度違い）
- **品質保証**: SSIM、色ヒストグラム相関、Keypointマッチングによる自動検証
- **カスタマイズ可能**: モデルの年代・性別・体型・ポーズ等を細かく指定
- **対話的修正**: チャット形式で生成後も自由に修正

## 動作環境

- Windows 10/11 (64bit)
- Python 3.10以上

## インストール

### 実行ファイル版（推奨）

1. [Releases](https://github.com/yourname/virtual-fashion-tryon/releases)から最新版をダウンロード
2. `VirtualFashionTryOn.exe`を実行

### ソースコード版

```bash
# リポジトリをクローン
git clone https://github.com/yourname/virtual-fashion-tryon.git
cd virtual-fashion-tryon

# 仮想環境を作成
python -m venv venv
venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt

# 環境変数を設定
copy .env.example .env
# .env ファイルを編集してAPIキーを設定

# 実行
python app/main.py
```

## APIキーの設定

初回起動時、または設定メニューからAPIキーを入力できます。

1. **OpenAI API Key**: https://platform.openai.com/api-keys
2. **Stability AI API Key**: https://platform.stability.ai/account/keys
3. **Google Cloud Service Account**: https://cloud.google.com/iam/docs/service-accounts

APIキーはWindows DPAPIで暗号化され、安全に保存されます。

## 使い方

1. 衣類画像をドラッグ&ドロップまたはファイル選択でアップロード
2. モデル属性を選択
   - **基本タブ**: 年代・性別・体型等
   - **ポーズタブ**: 画像ギャラリーから選択
   - **背景タブ**: 画像ギャラリーから選択
3. 生成設定
   - サイズと枚数を指定
   - **生成モード選択**: 種類違い or 角度違い
4. 「生成開始」ボタンをクリック
5. 結果を確認
6. **追加機能**（オプション）:
   - **チャットで修正**: 対話形式で画像を改善
   - **動画生成**: FASHN AIで高品質動画を生成 🎬✨
7. 保存

## 開発

```bash
# 開発用依存関係をインストール
pip install -e ".[dev]"

# テスト実行
pytest

# コードフォーマット
black .

# リンター
ruff check .
```

## ビルド

```bash
# PyInstallerでビルド
python -m PyInstaller --clean VirtualFashionTryOn.spec

# または PowerShellスクリプトを使用
.\scripts\pack_win.ps1
```

## ライセンス

MIT License

## サポート

問題が発生した場合は[Issues](https://github.com/yourname/virtual-fashion-tryon/issues)で報告してください。
