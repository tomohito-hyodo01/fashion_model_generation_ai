# クイックスタートガイド

## 🚀 最速起動（3ステップ）

### Windows PowerShell で実行

```powershell
# 1. セットアップ（初回のみ）
.\setup.ps1

# 2. 起動
.\run.ps1
```

それだけです！🎉

---

## 📖 詳細な手順

### 初回セットアップ（初回のみ実行）

1. **PowerShellを開く**
   - プロジェクトフォルダ（`fashion_model_generation_ai`）を右クリック
   - 「ターミナルで開く」または「PowerShellで開く」を選択

2. **セットアップスクリプトを実行**
   ```powershell
   .\setup.ps1
   ```
   
   もしエラーが出る場合：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\setup.ps1
   ```

3. **完了を待つ**
   - Python環境のチェック
   - 仮想環境の作成
   - 依存パッケージのインストール（数分かかります）

### アプリケーションの起動

```powershell
.\run.ps1
```

または

```powershell
# 仮想環境をアクティベート
.\venv\Scripts\Activate.ps1

# アプリを起動
python app/main.py
```

---

## 🔑 初回起動時の設定

### 1. APIキーダイアログが表示されます

使いたいAIサービスのAPIキーを入力：

#### OpenAI (DALL-E 3)
- 🔗 APIキー取得: https://platform.openai.com/api-keys
- 📝 形式: `sk-proj-...`
- 💰 コスト: $0.04～$0.12/枚

#### Stability AI
- 🔗 APIキー取得: https://platform.stability.ai/account/keys
- 📝 形式: `sk-...`
- 💰 コスト: $0.03/枚

#### Google Imagen
- 🔗 設定方法: https://cloud.google.com/vertex-ai/docs/start/introduction-unified-platform
- 📝 サービスアカウントJSONのパスを指定
- 💰 コスト: $0.04/枚

**💡 ヒント**: とりあえず1つだけでOK！後から追加できます。

### 2. テスト用画像を準備

サンプル画像の要件：
- ✅ PNG形式（推奨）
- ✅ 512x512以上
- ✅ 背景が白または透過
- ✅ 衣類が中心に配置

---

## 🎯 最初の生成テスト

1. **衣類画像を追加**
   - 「+ 画像を追加」ボタンをクリック
   - 画像を選択
   - タイプを選択（TOP/BOTTOM等）

2. **モデル属性を設定**
   - 性別: female
   - 年代: 20s
   - 国籍: asian
   - （その他はデフォルトでOK）

3. **生成設定**
   - AI: OpenAI (DALL-E 3)
   - 品質: standard
   - サイズ: 1024x1024
   - 枚数: 1

4. **「生成開始」をクリック！**

⏱️ 10～30秒で結果が表示されます。

---

## ❓ トラブルシューティング

### Q: `setup.ps1`が実行できない

```powershell
# 実行ポリシーを変更
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 再度実行
.\setup.ps1
```

### Q: Pythonがインストールされていない

1. https://www.python.org/downloads/ にアクセス
2. Python 3.10以上をダウンロード
3. インストール時に「Add Python to PATH」にチェック✅
4. インストール後、PowerShellを再起動

### Q: アプリは起動するが画像が生成されない

- APIキーが正しいか確認
- インターネット接続を確認
- APIキーに十分なクレジット（残高）があるか確認
- 初回生成は時間がかかる場合があります（最大60秒）

### Q: `ModuleNotFoundError`が出る

```powershell
# 仮想環境がアクティベートされているか確認
# プロンプトに (venv) が表示されているはず

# 依存パッケージを再インストール
pip install -r requirements.txt
```

---

## 📚 次のステップ

- 📖 [USAGE.md](USAGE.md) - 詳細な使用方法
- 🧪 複数枚生成を試す（枚数: 2～4）
- 🎨 異なるモデル属性で実験
- 💾 結果を保存

---

## 🆘 サポート

問題が解決しない場合：
1. [USAGE.md](USAGE.md) のトラブルシューティングを確認
2. GitHubのIssuesで質問
3. ログファイルを確認（存在する場合）

**Happy Generating! 🎉**



