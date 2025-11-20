# 参考人物機能 不具合修正レポート

**発見日**: 2025年11月15日  
**修正日**: 2025年11月15日

---

## 🐛 不具合の概要

### 事象

参考人物画像を設定しても、生成画像に反映されない。

**ログ**:
```
[Reference Person] 参考人物画像を設定: C:/Users/hyodo/Downloads/person.webp
...
=== Generating image 1/1 ===
  Added garment image: TOP: sample_jacket.jpg  ← 衣類のみ
  Sending request to Gemini 2.5 Flash Image...
```

**問題**: 
- "Added reference person image" のログが出ない
- 参考人物画像がGeminiに送信されていない

---

## 🔍 原因

### 根本原因

**参考人物画像がアダプターに設定されていませんでした**

```python
# MainWindow._start_generation()

adapter = self._create_adapter("gemini")  # アダプター作成
# ← ここで参考人物を設定すべきだが、設定されていない ❌

service = GenerateService(adapter, fidelity_checker)
# ← アダプターに参考人物画像がない状態でServiceに渡される
```

### 処理フロー（不具合時）

```
1. ユーザーが参考人物画像を設定
   ↓
2. self.reference_person_image = "path/to/person.jpg" ✅
   ↓
3. 生成開始ボタンをクリック
   ↓
4. adapter = create_adapter("gemini")
   adapter.reference_person_image = None  ← 未設定 ❌
   ↓
5. adapter.generate(garments, ...)
   ↓
6. self.reference_person_image をチェック
   → None なので参考人物なしとして処理 ❌
```

---

## ✅ 修正内容

### アダプター作成後に参考人物を設定

```python
# Geminiアダプタを作成
adapter = self._create_adapter("gemini")

# 参考人物画像をアダプターに設定 ← 追加！
if hasattr(adapter, 'set_reference_person'):
    if self.reference_person_image:
        print(f"[MainWindow] 参考人物をアダプターに設定: {self.reference_person_image}")
        adapter.set_reference_person(self.reference_person_image)
    else:
        print(f"[MainWindow] 参考人物なし（新しいモデルを生成）")
        adapter.set_reference_person(None)
```

### 修正後の処理フロー

```
1. ユーザーが参考人物画像を設定
   ↓
2. self.reference_person_image = "path/to/person.jpg" ✅
   ↓
3. 生成開始ボタンをクリック
   ↓
4. adapter = create_adapter("gemini")
   ↓
5. adapter.set_reference_person(self.reference_person_image)
   adapter.reference_person_image = "path/to/person.jpg" ✅
   ↓
6. adapter.generate(garments, ...)
   ↓
7. self.reference_person_image をチェック
   → "path/to/person.jpg" なので参考人物画像を送信 ✅
```

---

## 📊 修正前後の比較

### Before（修正前）

```
ログ:
  [Reference Person] 参考人物画像を設定: person.jpg
  ...
  Added garment image: TOP: shirt.png
  ← 参考人物が送信されていない

Geminiへの送信:
  [服の画像]
  "Create a NEW fashion model..."  ← 新しいモデルを生成
```

### After（修正後）

```
ログ:
  [Reference Person] 参考人物画像を設定: person.jpg
  [MainWindow] 参考人物をアダプターに設定: person.jpg
  ...
  Added reference person image: person.jpg  ← 追加される！
  Added garment image: TOP: shirt.png

Geminiへの送信:
  [参考人物の画像]  ← 最初に送信
  [服の画像]
  "Put these clothes onto the SAME PERSON from image 1..."  ← 人物を保持
```

---

## 🧪 確認方法

### デバッグログ

修正後は、以下のログが出力されます：

```
[Reference Person] 参考人物画像を設定: C:/path/to/person.jpg
[MainWindow] 参考人物をアダプターに設定: C:/path/to/person.jpg
...
=== Generating image 1/1 ===
  Selected pose: front → standing straight, facing camera
  Selected background: white → plain solid white background
  Added reference person image: person.jpg  ← このログが重要！
  Added garment image: TOP: sample_jacket.jpg
  Sending request to Gemini 2.5 Flash Image...
```

### 確認ポイント

✅ 「[MainWindow] 参考人物をアダプターに設定」が表示される  
✅ 「Added reference person image」が表示される  
✅ 生成画像が参考人物と同じ顔・体型になる  

---

## 📝 修正ファイル

| ファイル | 修正内容 |
|---------|---------|
| `app/ui/main_window.py` | アダプター作成後に参考人物を設定 |
| `app/core/adapters/gemini_imagen_adapter.py` | スタンドアロン実行対応（パス調整） |

---

## ✅ 修正完了

参考人物画像が正しくGeminiに送信されるようになりました！

**次回起動時から正常に動作します。**

---

**修正完了日時**: 2025年11月15日  
**ステータス**: ✅ 修正完了

