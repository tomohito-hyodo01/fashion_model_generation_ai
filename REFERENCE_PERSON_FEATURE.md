# 参考人物機能 実装ガイド

**実装日**: 2025年11月15日  
**機能名**: 参考人物に服を着せる機能

---

## ✨ 新機能の概要

### 従来の動作（参考人物なし）

```
入力: 服の画像のみ
  ↓
Gemini: 新しいモデルを生成
  ↓
出力: その服を着た新しいモデル
```

### 新機能（参考人物あり）

```
入力: 参考人物の画像 + 服の画像
  ↓
Gemini: 参考人物に服を着せる
  ↓
出力: 同じ人物が服を着た画像
```

---

## 🎯 ユースケース

### ケース1: 特定の人物でのフィッティング

```
【目的】
自分自身やクライアントの写真に服を着せたい

【操作】
1. 「👤 参考人物」エリアで人物画像をアップロード
2. 「衣類画像」エリアで試着したい服をアップロード
3. 生成開始

【結果】
- 参考人物と同じ顔・体型
- 指定した服を着用
- 違和感のない合成
```

### ケース2: モデルの一貫性

```
【目的】
同じモデルで複数の衣類を試したい

【操作】
1. 気に入ったモデルの画像を参考人物として設定
2. 異なる衣類で複数回生成

【結果】
- すべて同じモデルで統一
- コーディネート提案に最適
```

---

## 🎨 新しいUI構造

### メインウィンドウ

```
┌──────────────┬──────────────┬─────────────────────────┐
│👤 参考人物   │ 衣類画像     │ モデル属性              │
│              │              │ [基本][ポーズ][背景]    │
│[人物画像]    │ [+ 追加]     │                         │
│              │              │  ギャラリー表示         │
│ [📁 選択]    │ [服1]        │                         │
│ [✕ クリア]   │ [服2]        │                         │
│              │              │                         │
│💡 ヒント:    │              │                         │
│全身写真推奨  │              │                         │
└──────────────┴──────────────┴─────────────────────────┘
```

### 参考人物エリア

```
┌─────────────────────────────────┐
│  👤 参考人物画像                │
├─────────────────────────────────┤
│  人物の画像を指定すると、       │
│  その人物に服を着せた画像を     │
│  生成します。                   │
├─────────────────────────────────┤
│  ┌─────────────────────┐       │
│  │                     │       │
│  │  [プレビュー画像]   │       │
│  │                     │       │
│  └─────────────────────┘       │
├─────────────────────────────────┤
│  [📁 人物画像を選択] [✕ クリア] │
├─────────────────────────────────┤
│  💡 ヒント:                     │
│  ・全身が写っている画像が最適   │
│  ・顔がはっきり見える画像を使用 │
│  ・背景がシンプルな画像を推奨   │
└─────────────────────────────────┘
```

---

## 🔧 実装の詳細

### データフロー

#### パターン1: 参考人物なし（従来通り）

```
[服1の画像]
[服2の画像]
↓
Gemini API
↓
プロンプト:
"Create a photograph of a fashion model.
 The model MUST wear these clothing items..."
↓
新しいモデルを生成
```

#### パターン2: 参考人物あり（新機能）

```
[参考人物の画像] ← 最初に配置
[服1の画像]
[服2の画像]
↓
Gemini API
↓
プロンプト:
"Look at the FIRST image showing a PERSON.
 Look at the NEXT 2 images showing CLOTHING.
 CREATE: Put these clothes onto the SAME PERSON from image 1.
 PRESERVE THE PERSON: Keep the EXACT SAME face, hair, skin tone..."
↓
同じ人物が服を着た画像
```

### Geminiへの送信内容

```python
# 参考人物ありの場合
prompt_parts = [
    <PIL.Image: 参考人物>,      # 画像1
    <PIL.Image: Tシャツ>,       # 画像2
    <PIL.Image: ジーンズ>,      # 画像3
    """
    CRITICAL INSTRUCTIONS:
    1. Look at the FIRST image showing a PERSON (reference person).
    2. Look at the NEXT 2 image(s) showing CLOTHING items.
    3. CREATE A PHOTOGRAPH: Put the clothing items from images 2-3 
       onto the SAME PERSON from image 1.
    4. PRESERVE THE PERSON: Keep the EXACT SAME face, hair, 
       skin tone, and body features from the reference person image.
    5. PRESERVE THE CLOTHING: Copy the EXACT clothing items...
    """
]
```

---

## 📊 プロンプトの比較

### 参考人物なしの場合

```
1. Look at the 2 reference image(s) above showing clothing items.
2. Create a photograph of a 20s asian female fashion model.
3. The model MUST wear the EXACT SAME clothing items...
```

**ポイント**: 新しいモデルを生成

### 参考人物ありの場合

```
1. Look at the FIRST image showing a PERSON (reference person).
2. Look at the NEXT 2 image(s) showing CLOTHING items.
3. CREATE A PHOTOGRAPH: Put the clothing items from images 2-3 
   onto the SAME PERSON from image 1.
4. PRESERVE THE PERSON: Keep the EXACT SAME face, hair, 
   skin tone, and body features...
5. PRESERVE THE CLOTHING: Copy the EXACT clothing items...
```

**ポイント**: 参考人物を保持しながら服を変更

---

## 🎯 使用方法

### 基本的な使い方

#### ステップ1: 参考人物画像をアップロード

1. 左上の「👤 参考人物」エリアを確認
2. 「📁 人物画像を選択」ボタンをクリック
3. 人物の写真を選択
4. プレビューに表示される

**推奨画像**:
- ✅ 全身が写っている
- ✅ 顔がはっきり見える
- ✅ 背景がシンプル
- ✅ 正面または斜め前から撮影

#### ステップ2: 衣類画像をアップロード

1. 「衣類画像」エリアで「+ 画像を追加」
2. 試着したい服の画像を選択
3. 複数の服を追加可能

#### ステップ3: 設定と生成

1. モデル属性を設定（ポーズ・背景等）
2. 生成開始

#### ステップ4: 結果確認

- ✅ 参考人物と同じ顔・体型
- ✅ 指定した服を着用
- ✅ 自然な仕上がり

---

## 💡 実装のポイント

### 1. 画像の順序が重要

```python
# 必ず参考人物を最初に配置
prompt_parts = [
    <参考人物画像>,  # 1番目
    <服の画像1>,     # 2番目
    <服の画像2>,     # 3番目
    <プロンプト>
]
```

### 2. プロンプトで明確に指示

```
"Look at the FIRST image showing a PERSON"
  ↑ 1枚目が人物であることを明示

"Put the clothing items from images 2-3 onto the SAME PERSON"
  ↑ 2-3枚目の服を1枚目の人物に着せることを明示
```

### 3. 人物の保持を強調

```
"PRESERVE THE PERSON: Keep the EXACT SAME face, hair, 
 skin tone, and body features"
  ↑ 人物の特徴を変えないように強く指示
```

---

## 🧪 テスト

### 参考人物機能のテスト

```bash
python app/main.py
```

**テスト手順**:

1. **参考人物を設定**
   - 人物の全身写真をアップロード
   - プレビューに表示される

2. **衣類を追加**
   - Tシャツの画像をアップロード

3. **生成**
   - 生成開始ボタンをクリック

4. **コンソールログを確認**:
   ```
   Added reference person image: person.jpg
   Added garment image: TOP: shirt.png
   Look at the FIRST image showing a PERSON
   Put the clothing items onto the SAME PERSON
   ```

5. **結果を確認**:
   - ✅ 参考人物と同じ顔
   - ✅ 指定した服を着用

---

## 📋 作成されたファイル

| ファイル | 説明 |
|---------|------|
| `app/models/reference_person.py` | 参考人物データモデル |
| `app/ui/widgets/reference_person_widget.py` | 参考人物UIウィジェット |
| `app/core/adapters/gemini_imagen_adapter.py` | Geminiアダプター更新 |
| `app/ui/main_window.py` | メインウィンドウ統合 |
| `REFERENCE_PERSON_FEATURE.md` | このドキュメント |

---

## 🆚 モード比較

### モード1: 参考人物なし（従来）

**用途**:
- 様々なモデルで試したい
- モデルの属性を細かく指定したい
- 新しいモデルを生成したい

**メリット**:
- モデル属性を自由に設定
- 様々なバリエーション

### モード2: 参考人物あり（新機能）

**用途**:
- 特定の人物で試着したい
- 自分やクライアントの写真を使用
- モデルの一貫性が必要

**メリット**:
- 同じ人物で統一
- パーソナライズされた結果
- リアルな試着体験

---

## 🎬 動画生成との連携

参考人物機能は**動画生成にも対応**しています！

```
1. 参考人物 + 服で画像を生成
2. 生成画像を選択
3. 「🎬 動画を生成」で動画化
4. 参考人物が動く動画が完成！
```

---

## 📝 注意事項

### 良い結果を得るために

✅ **推奨**:
- 全身が写っている画像
- 顔がはっきり見える
- 背景がシンプル
- 照明が良い

❌ **非推奨**:
- 顔が隠れている
- 複数人が写っている
- 背景が複雑
- 暗い画像

### 制限事項

- 参考人物の体型に合わない服の場合、不自然になる可能性
- Gemini AIの理解度に依存
- 完全な再現は保証されない

---

## 🎊 機能追加まとめ

### 実装内容

✅ **参考人物データモデル** - ReferencePerson  
✅ **参考人物UI** - ReferencePersonWidget  
✅ **メインウィンドウ統合** - レイアウト変更  
✅ **Geminiアダプター対応** - 参考人物画像の送信  
✅ **プロンプト最適化** - 「この人物に服を着せる」指示  

### 使用方法

1. 参考人物画像をアップロード
2. 衣類画像をアップロード
3. 生成開始
4. 参考人物が服を着た画像が生成される

---

## 📊 機能一覧更新

### 全実装機能（18機能）

| Phase | 機能 |
|-------|------|
| Phase 1 | ポーズギャラリー、背景ギャラリー、MediaPipe、カスタム画像 (5機能) |
| Phase 2 | マルチアングル、チャット修正、自然言語解析 (5機能) |
| Phase 3 | 履歴管理、プロジェクト管理、色変更、バッチ処理、設定管理 (6機能) |
| Phase 4 | FASHN AI動画生成 (1機能) |
| **Phase 5** | **参考人物に服を着せる機能 (1機能)** ✨ |

**合計**: **18機能**

---

## 🚀 すぐに使える！

```bash
python app/main.py
```

新機能をお試しください！

1. 左上の「👤 参考人物」で人物画像を選択
2. 「衣類画像」で服を追加
3. 生成！

---

**Phase 5実装完了！** 🎊

