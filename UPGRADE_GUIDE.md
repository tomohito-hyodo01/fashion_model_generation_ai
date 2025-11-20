# アップグレードガイド v1.0 → v1.1

## 🎉 主な改善点

### ⭐ Stability AI SD 3.5（image-to-image機能）
- **衣類画像を直接参照**できるようになりました
- テキスト記述のみの旧版と比べて**忠実度が大幅に向上**
- 衣類の色・柄・質感をより正確に再現

### ⭐ Google Imagen 4対応
- 最新のImagen 4.0モデルに更新
- Gemini API経由で簡単に使用可能（APIキーのみ）
- より高い写実性と人物生成品質

---

## 🔄 更新手順

### 1. コードを更新

既にアップデート済みです！以下が変更されています：

```
✅ Stability AI: SDXL 1.0 → SD 3.5 Large
✅ Google: Imagen 3 → Imagen 4.0
✅ 新機能: image-to-image対応
```

### 2. 依存パッケージを更新

```powershell
# 仮想環境をアクティベート
.\venv\Scripts\Activate.ps1

# パッケージを更新
pip install -r requirements.txt --upgrade
```

### 3. アプリケーションを再起動

```powershell
python app/main.py
```

---

## 📝 使用方法の変更

### 🆕 Stability AI SD 3.5の使い方

**従来（v1.0）:**
- テキストプロンプトのみで生成
- 衣類の色分析 → テキスト記述 → 生成

**新機能（v1.1）:**
1. 衣類画像を追加
2. **Stability AI SD 3.5**を選択
3. 生成開始
4. → **衣類画像が参照画像として送信される** ✨
5. → **その衣類を着たモデルが生成される**

**メリット:**
- ✅ 色の正確性が大幅に向上
- ✅ 柄やテクスチャも忠実に再現
- ✅ 全体的なデザインが保持される

---

## 🎯 推奨設定

### 最良の結果を得るために

**プロバイダ選択:**
1. **第1優先: Stability AI SD 3.5** ⭐
   - 画像参照機能あり
   - 最も忠実な再現

2. **第2優先: Google Imagen 4**
   - 高品質な写実性
   - テキストのみだが性能向上

3. **第3優先: OpenAI DALL-E 3**
   - 自然な仕上がり
   - テキストのみ

**設定:**
- 品質: **hd**
- サイズ: **1024x1792**（全身写真に最適）
- 枚数: **2-4枚**（複数生成して最良を選択）

---

## 🔑 APIキーについて

### Google Imagen 4の簡易設定

**新機能: Gemini API Keyで簡単に使用可能！**

1. https://aistudio.google.com/apikey にアクセス
2. APIキーを生成（無料枠あり）
3. アプリのAPIキー設定で入力

**従来のVertex AI方式（本格運用）:**
- サービスアカウントJSONファイルが必要
- Google Cloudプロジェクトが必要
- より高度な制御が可能

---

## 💰 コスト変更

| プロバイダ | v1.0 | v1.1 |
|-----------|------|------|
| OpenAI DALL-E 3 | $0.040-$0.120 | 変更なし |
| Stability AI | $0.030 (SDXL 1.0) | $0.065 (SD 3.5) |
| Google Imagen | $0.040 (Imagen 3) | $0.040 (Imagen 4) |

**注:** SD 3.5はコストが上がりますが、画像参照機能により**品質が大幅に向上**します。

---

## 🐛 既知の問題と解決策

### Q: SD 3.5でエラーが出る

**解決策:**
- Stability AIのAPIキーが最新か確認
- SD 3.5へのアクセス権限があるか確認
- 必要に応じてStability AIのダッシュボードで確認

### Q: Gemini APIで403エラー

**解決策:**
- APIキーが正しいか確認
- https://aistudio.google.com/apikey で新しいキーを生成
- APIが有効化されているか確認

### Q: 画像参照が機能しない

**確認事項:**
- **Stability AI SD 3.5**を選択しているか
- 衣類画像が正しく追加されているか
- ファイルサイズが適切か（推奨: 5MB以下）

---

## 📚 参考リンク

- [Stability AI SD 3.5 Documentation](https://platform.stability.ai/docs)
- [Google Imagen 4 Documentation](https://ai.google.dev/gemini-api/docs/imagen)
- [Gemini API Key取得](https://aistudio.google.com/apikey)

---

**Happy Upgrading! 🚀**



