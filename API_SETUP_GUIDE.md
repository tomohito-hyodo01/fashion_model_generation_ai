# APIキー設定ガイド

このガイドでは、各プロバイダのAPIキーの取得方法を説明します。

---

## ⭐ Stability AI SD 3.5（最推奨）

### なぜ推奨？
- **画像参照機能**: 衣類画像を直接参照して忠実に再現
- 最も正確な衣類再現が可能

### 取得手順

1. **アカウント作成**
   - https://platform.stability.ai/ にアクセス
   - 「Sign Up」でアカウント作成

2. **クレジット購入**
   - 初回は$10程度のクレジット購入が必要
   - クレジットカードで支払い

3. **APIキー取得**
   - https://platform.stability.ai/account/keys にアクセス
   - 「Create API Key」をクリック
   - キーをコピー（`sk-...`の形式）

4. **アプリに設定**
   - アプリの「APIキー設定」で入力
   - または`.env`ファイルに`STABILITY_API_KEY=sk-...`と記載

### 料金
- SD 3.5 Large: **$0.065/枚**
- SD 3.5 Turbo: **$0.040/枚**
- 従量課金（使った分だけ）

---

## 🔷 Google Imagen 4

### 方法1: Gemini API（簡易・推奨）

**最も簡単！APIキーだけで使用可能**

1. **APIキー取得**
   - https://aistudio.google.com/apikey にアクセス
   - Googleアカウントでログイン
   - 「Get API Key」をクリック
   - 「Create API key」を選択

2. **無料枠**
   - 毎月一定の無料リクエストあり
   - 超過分は従量課金

3. **アプリに設定**
   - アプリの「APIキー設定」で入力
   - Gemini API Keyの欄に貼り付け

### 方法2: Vertex AI（本格運用）

**Google Cloudプロジェクトが必要**

1. **Google Cloudプロジェクト作成**
   - https://console.cloud.google.com/
   - 新しいプロジェクトを作成

2. **Vertex AIを有効化**
   - 「APIs & Services」→「Enable APIs」
   - 「Vertex AI API」を検索して有効化

3. **サービスアカウント作成**
   - 「IAM & Admin」→「Service Accounts」
   - サービスアカウントを作成
   - JSONキーをダウンロード

4. **アプリに設定**
   - JSONファイルのパスを指定

### 料金
- Standard: **$0.040/枚**
- Ultra: **$0.080/枚**
- Fast: **$0.020/枚**

---

## 🤖 OpenAI DALL-E 3

### 取得手順

1. **アカウント作成**
   - https://platform.openai.com/ にアクセス
   - 「Sign up」でアカウント作成

2. **クレジット購入**
   - 「Billing」→「Add payment method」
   - 初回$5〜$10のクレジット購入推奨

3. **APIキー作成**
   - https://platform.openai.com/api-keys
   - 「Create new secret key」をクリック
   - キーをコピー（`sk-proj-...`の形式）

4. **アプリに設定**
   - アプリの「APIキー設定」で入力

### 料金
- 1024x1024 standard: **$0.040/枚**
- 1024x1024 hd: **$0.080/枚**
- 1024x1792/1792x1024 hd: **$0.120/枚**

---

## 🔐 セキュリティ

### APIキーの保護

アプリは以下の方法でAPIキーを保護します：

1. **Windows DPAPI暗号化**
   - ユーザーアカウントとマシンにバインド
   - 他のユーザーやPCでは復号化不可

2. **Fernet暗号化（フォールバック）**
   - Windows以外の環境でも動作
   - 暗号化キーは安全に保存

### 注意事項

- ❌ APIキーを他人と共有しない
- ❌ GitHubなどに`.env`をアップロードしない（`.gitignore`に含まれています）
- ✅ 定期的にAPIキーをローテーション
- ✅ 使用量を定期的に確認

---

## 💰 コスト管理

### 推奨設定（コスト最適化）

**テスト・実験時:**
- Stability AI SD 3.5: $0.065/枚
- 枚数: 1枚
- 品質: standard

**本番・重要な生成:**
- Stability AI SD 3.5: $0.065/枚
- 枚数: 2-4枚（最良を選択）
- 品質: hd

### 使用量の確認

各プロバイダのダッシュボードで確認：
- Stability AI: https://platform.stability.ai/account/credits
- Google: https://console.cloud.google.com/billing
- OpenAI: https://platform.openai.com/usage

---

## 🆘 トラブルシューティング

### Stability AI: 403 Forbidden
- APIキーが正しいか確認
- SD 3.5へのアクセス権限があるか確認
- クレジット残高を確認

### Google: 認証エラー
- Gemini API Keyが正しいか確認
- APIが有効化されているか確認
- https://aistudio.google.com/apikey で再発行

### OpenAI: 401 Unauthorized
- APIキーが正しいか確認（`sk-proj-`で始まる）
- 組織IDが必要な場合は設定
- クレジット残高を確認

---

**サポート:** APIキーに関する問題は、各プロバイダのサポートにお問い合わせください。




