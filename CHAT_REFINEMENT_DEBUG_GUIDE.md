# チャット修正機能 デバッグガイド

**作成日**: 2025年11月15日

---

## 🔍 デバッグログの確認

修正後、チャット機能が正しく動作しているかは、以下のログで確認できます：

### 期待されるログ

```
【ユーザーが「もっと明るくして」と入力】

[Chat] 修正要求: もっと明るくして

[Chat Refinement] ユーザー指示: もっと明るくして

[Chat Parser] Gemini生レスポンス:
{
  "changes": {
    "lighting": "bright, well-lit",
    "prompt_additions": "brighter lighting, increased brightness"
  },
  "ai_response": "承知しました。明るさを上げて画像を再生成します。"
}

[Chat Parser] 解析結果: {...}

[Chat Parser] apply_modifications - 入力changes: {...}
[Chat Parser] パラメータ更新: lighting = bright, well-lit
[Chat Parser] custom_description更新(lighting): ... lighting: bright, well-lit
[Chat Parser] パラメータ更新: prompt_additions = brighter lighting...
[Chat Parser] custom_description更新: ... brighter lighting, increased brightness
[Chat Parser] apply_modifications - 出力params: {...}

[Chat Refinement] 変更内容: {...}
[Chat Refinement] AI応答: 承知しました...
[Chat Refinement] 元のcustom_description: Pose: ... Background: ...
[Chat Refinement] 更新後custom_description: Pose: ... Background: ... lighting: bright, well-lit brighter lighting...
[Chat Refinement] 最終ModelAttributes:
  - pose: front
  - background: white
  - custom_description: ...lighting...bright...

=== Generating image 1/1 ===
  Selected pose: front → standing straight...
  Custom description: Pose: ... Background: ... lighting: bright, well-lit brighter lighting...
  ← ここに指示が含まれているか確認！
```

---

## 🎯 確認ポイント

### 1. Gemini APIの解析結果

```
[Chat Parser] Gemini生レスポンス:
```

このログでGeminiが正しくJSON形式で返しているか確認

### 2. パラメータの更新

```
[Chat Parser] パラメータ更新: lighting = ...
[Chat Parser] custom_description更新: ...
```

このログで変更が適用されているか確認

### 3. Geminiへの送信

```
Custom description: Pose: ... Background: ... lighting: bright...
```

このログで指示がプロンプトに含まれているか確認

---

## 🐛 問題が起こる可能性

### パターン1: Geminiが解析していない

**症状**:
```
[Chat Parser] 解析結果: {"prompt_additions": "もっと明るくして"}
```

**原因**: Gemini APIがJSON形式で返していない

**対策**: プロンプトを調整、またはフォールバック処理

### パターン2: パラメータが適用されていない

**症状**:
```
[Chat Refinement] 更新後custom_description: Pose: ... Background: ...
← lighting の指示が含まれていない
```

**原因**: apply_modificationsで正しく適用されていない

**対策**: コードのロジックを修正

### パターン3: Geminiに反映されていない

**症状**:
```
Custom description: Pose: ... Background: ... lighting: bright...
← 指示は含まれている

しかし生成画像が変わらない
```

**原因**: Geminiがcustom_descriptionを無視している

**対策**: プロンプト構築方法を変更

---

## 🧪 テスト手順

### 1. アプリケーションを再起動

```bash
python app/main.py
```

### 2. 画像を生成

1. 衣類画像をアップロード
2. 通常通り生成

### 3. チャットで修正

1. 生成画像の「この画像を修正」をクリック
2. チャット欄に「もっと明るくして」と入力
3. 送信

### 4. コンソールログを確認

上記のデバッグログがすべて表示されるか確認

---

## 📝 修正内容

### 追加されたデバッグログ

1. **Gemini生レスポンス**の表示
2. **パラメータ更新**の詳細ログ
3. **custom_description更新**の確認
4. **最終ModelAttributes**の出力

これらのログで、どこで問題が起きているか特定できます。

---

**アプリケーションを再起動して、チャット機能を試してください。**

コンソールログを確認して、結果をお知らせください。

