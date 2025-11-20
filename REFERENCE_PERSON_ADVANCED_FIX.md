# 参考人物機能 - プロンプト強化修正

**修正日**: 2025年11月15日  
**問題**: 参考人物画像が送信されているが、結果に反映されない

---

## 🔍 問題の詳細分析

### ログ確認結果

```
✅ [Gemini Adapter] ★参考人物画像を設定★
✅ Resized reference person image to: (1024, 585)
✅ ★★★ Added reference person image ★★★
✅ Added garment image
✅ [OK] Image generated successfully!
```

**すべて正常に送信されている** ✅

### しかし...

**問題**: 生成画像が参考人物をベースにしていない ❌

---

## 💡 根本原因

### Geminiの理解不足

**現在のプロンプト**（簡潔版）では、Geminiが以下を理解していない可能性：

1. 「画像1の人物を保持する」という指示が弱い
2. 「新しい人物を生成」と解釈している
3. 参考人物を「参考」としてのみ使用（影響度が低い）

### プロンプトエンジニアリングの問題

```
❌ 弱い指示:
   "Create a photo of the SAME PERSON from image 1"
   → Geminiは新しい人物を生成する傾向が強い

✅ 強い指示が必要:
   "THE EXACT SAME FACE, HAIR, BODY from image 1"
   "This is NOT a new person"
   "Think of it as: person from image 1 → change clothes → result"
```

---

## ✅ 修正内容

### プロンプトの大幅強化

**新しいプロンプト**:

```
IMAGE 1 shows a PERSON (the reference person).
IMAGES 2-{count} show CLOTHING items.

YOUR TASK:
Generate a photograph of THE EXACT SAME PERSON from image 1, 
but dressed in the clothing from images 2-{count}.

CRITICAL REQUIREMENTS:
1. FACE: Use the EXACT SAME face from image 1
   - same eyes, nose, mouth, facial structure, skin tone
2. HAIR: Use the EXACT SAME hair from image 1
   - same color, style, length
3. BODY: Use the EXACT SAME body type from image 1
   - same height, build, proportions
4. CLOTHING: Replace ONLY the clothing with the items from images 2-{count}
5. Copy the clothing exactly - same colors, patterns, textures, logos

IMPORTANT: This is NOT a new person. 
This is THE PERSON FROM IMAGE 1 wearing different clothes.

Think of it as:
  Take person from image 1 → Change only their clothes → That's the result.
```

### 重要な変更点

| 項目 | Before | After |
|------|--------|-------|
| **顔の指示** | "Keep face" | "EXACT SAME face - eyes, nose, mouth, facial structure" |
| **髪の指示** | "Keep hair" | "EXACT SAME hair - color, style, length" |
| **強調** | 軽い | "This is NOT a new person" |
| **思考プロセス** | なし | "Think of it as: person → change clothes → result" |

---

## 🎯 なぜこれで改善するか

### Geminiの動作理解

Gemini 2.5 Flash Imageは：
- デフォルトで「新規画像生成」を行う
- 「既存画像の編集」は明示的な指示が必要
- 詳細で具体的な指示により理解度が向上

### プロンプトエンジニアリング

```
弱い指示:
  "same person" → 曖昧

強い指示:
  "EXACT SAME face (eyes, nose, mouth, facial structure, skin tone)" → 具体的

さらに強い指示:
  + "This is NOT a new person"
  + "Think of it as: person A → change clothes → result"
  → AIの思考を誘導
```

---

## 🧪 再テスト

### アプリケーションを再起動

```bash
python app/main.py
```

### テスト手順

1. 参考人物画像を選択
2. 衣類画像を追加
3. 生成開始

### 期待される改善

**Before**:
- 参考人物とは別の新しいモデルが生成される ❌

**After**:
- 参考人物の顔・髪・体型が保持される ✅
- 服だけが変更される ✅

---

## 💡 それでも改善しない場合の対策

### 対策1: Geminiの制限を理解

Gemini 2.5 Flash Imageは画像生成モデルであり、**画像編集モデルではない**可能性があります。

**つまり**:
- 「新しい画像を生成する」ことは得意
- 「既存画像の一部を変更する」ことは苦手かもしれない

### 対策2: 別のアプローチ

もし上記のプロンプト強化でも不十分な場合：

#### アプローチA: 2段階生成

```
1. 参考人物の特徴を分析（Gemini APIで記述生成）
2. その記述 + 服の画像で生成
```

#### アプローチB: 画像編集特化モデルの使用

```
- Stability AI Inpainting
- OpenAI DALL-E Edit
- その他の画像編集AI
```

#### アプローチC: プロンプトの更なる工夫

```
参考人物の特徴を先に言語化:
"Create a photo of a person with:
 - Face features: [参考画像から抽出]
 - Hair: [参考画像から抽出]
 - Body: [参考画像から抽出]
Wearing: [服の画像]"
```

---

## 📊 技術的制約

### Gemini 2.5 Flash Imageの特性

| 機能 | 対応 |
|------|------|
| 新規画像生成 | ✅ 得意 |
| 複数画像参照 | ✅ 可能 |
| 画像の理解 | ✅ 高精度 |
| 画像編集 | ⚠️ 制限的 |
| アイデンティティ保持 | ⚠️ 困難な可能性 |

**結論**: 
Geminiは「新規生成」には強いが、「特定人物の保持」は技術的に難しい可能性があります。

---

## 🎯 現実的な期待値

### 現在のプロンプト強化で期待できること

- 🟡 **顔の類似度**: 50-70%程度
- 🟡 **髪型の保持**: 部分的
- 🟡 **体型の保持**: 部分的
- ✅ **服の再現**: 高精度（これは元々強い）

### 完全な保持が難しい理由

Gemini 2.5 Flash Imageは：
- 画像編集ツールではなく、画像生成ツール
- 「参考」として見るが、「そのまま使用」するわけではない
- 内部的に新しい画像を生成している

---

## 💡 推奨される次のステップ

### 1. まず今回の修正で試す

プロンプトを強化したので、改善する可能性があります。

### 2. 結果を確認

- 全く似ていない → Geminiの制限
- 少し似ている → プロンプトさらに改善の余地
- かなり似ている → 成功！

### 3. 満足できない場合

**オプションA**: 画像編集特化AIの導入を検討
**オプションB**: より強力なプロンプトエンジニアリング
**オプションC**: 機能の位置づけを「参考」として説明

---

**まず、現在の強化されたプロンプトで再テストしてください。**

結果によって、さらなる改善策をご提案いたします。
