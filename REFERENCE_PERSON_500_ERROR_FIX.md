# 参考人物機能 500エラー修正レポート

**発生日**: 2025年11月15日  
**修正日**: 2025年11月15日

---

## 🐛 エラーの概要

### 事象

参考人物画像は正しくGeminiに送信されているが、500エラーが発生。

**エラーメッセージ**:
```
google.api_core.exceptions.InternalServerError: 500 An internal error has occurred
```

**ログ確認結果**:
```
✅ [Gemini Adapter] ★参考人物画像を設定★
✅ ★★★ Added reference person image ★★★
✅ Added garment image
✅ Sending request to Gemini 2.5 Flash Image...
❌ 500 Internal Server Error
```

**結論**: 画像は送信されているが、Gemini側で処理エラー

---

## 🔍 原因分析

### 可能性の高い原因

| 原因 | 可能性 | 説明 |
|------|--------|------|
| **画像サイズ** | 🔴 高 | 参考人物画像が大きすぎる可能性 |
| **画像形式** | 🟡 中 | webp形式の互換性問題 |
| **プロンプト** | 🟡 中 | プロンプトが複雑すぎる |
| **API制限** | 🟢 低 | 同時送信画像数の制限 |

### 発生したケース

```
入力画像:
  - 参考人物: look-scene02-01.limCyzOx_Z18xo6j.webp
  - 衣類: sample_jacket.jpg
  
結果: 500 Internal Server Error
```

---

## ✅ 修正内容

### 1. 画像サイズの制限

```python
# 参考人物画像のサイズを制限（1024px以下に）
max_size = 1024
if max(person_img.size) > max_size:
    ratio = max_size / max(person_img.size)
    new_size = tuple(int(dim * ratio) for dim in person_img.size)
    person_img = person_img.resize(new_size, Image.Resampling.LANCZOS)
    print(f"  Resized reference person image to: {new_size}")
```

### 2. RGB形式に変換

```python
# webp等の特殊形式をRGBに変換
person_img = person_img.convert('RGB')
```

### 3. プロンプトの簡潔化

**Before（複雑）**:
```
CRITICAL INSTRUCTIONS:
1. Look at the FIRST image showing a PERSON (reference person).
2. Look at the NEXT 2 image(s) showing CLOTHING items.
3. CREATE A PHOTOGRAPH: Put the clothing items from images 2-3 onto the SAME PERSON from image 1.
4. PRESERVE THE PERSON: Keep the EXACT SAME face, hair, skin tone, and body features...
5. PRESERVE THE CLOTHING: Copy the EXACT clothing items...
... (11項目)
```

**After（簡潔）**:
```
Look at image 1: A PERSON.
Look at image(s) 2-3: CLOTHING items.

Task: Create a photo of the SAME PERSON from image 1, 
wearing the EXACT clothes from the other images.

Key points:
- Keep the person's face, hair, and body from image 1
- Put on the exact clothes from images 2-3
- Pose: standing straight
- Background: white
- Full body shot, professional photography
```

### 4. 履歴保存エラーの修正

```python
# ClothingItemオブジェクトを辞書に変換
json_safe_params = {}
for key, value in self.last_generation_params.items():
    if key == "garments":
        json_safe_params[key] = [g.to_dict() for g in value]  # オブジェクト→辞書
    else:
        json_safe_params[key] = value
```

---

## 🧪 再テスト手順

### 1. アプリケーションを再起動

```bash
python app/main.py
```

### 2. 参考人物機能をテスト

1. **小さめの画像を使用**:
   - 推奨: 1000x1500px以下
   - 形式: JPGまたはPNG

2. **参考人物を設定**

3. **衣類を追加**

4. **生成開始**

5. **ログを確認**:
   ```
   Resized reference person image to: (724, 1024)  ← サイズ制限
   ★★★ Added reference person image: person.jpg ★★★
   Added garment image: TOP: shirt.png
   Sending request to Gemini 2.5 Flash Image...
   [OK] Image generated successfully!  ← 成功！
   ```

---

## 💡 500エラーの回避策

### 方法1: 画像サイズを小さくする（推奨）

**自動的に実施**:
- 修正により、1024px以下に自動リサイズ

### 方法2: シンプルな画像を使用

**推奨画像**:
- ✅ 背景がシンプル
- ✅ 人物が1人のみ
- ✅ 全身が写っている
- ✅ 解像度: 800x1200px程度

**非推奨画像**:
- ❌ 背景が複雑
- ❌ 複数人が写っている
- ❌ 超高解像度（4K等）
- ❌ 特殊な形式（webp等）

### 方法3: 参考人物なしで試す

まず参考人物なしで生成が成功するか確認：

1. 参考人物を**設定しない**
2. 衣類のみで生成
3. 成功したら、参考人物を追加してみる

---

## 📊 テスト結果（期待）

### 成功ケース

```
入力:
  - 参考人物: person.jpg (800x1200, PNG)
  - 衣類: shirt.png

ログ:
  Resized reference person image to: (682, 1024)
  ★★★ Added reference person image: person.jpg ★★★
  Added garment image: TOP: shirt.png
  [OK] Image generated successfully!

結果:
  参考人物が服を着た画像 ✅
```

---

## 🔧 その他の修正

### 履歴保存エラーの修正

**エラー**:
```
[History] 履歴保存エラー: Object of type ClothingItem is not JSON serializable
```

**原因**:
- ClothingItemオブジェクトがJSON化できない

**修正**:
- ClothingItem → 辞書に変換してから保存

**効果**:
- ✅ 履歴保存が正常に動作

---

## 🎯 まとめ

### 修正内容

1. ✅ 参考人物画像のサイズ制限（1024px以下）
2. ✅ RGB形式への変換（形式問題を回避）
3. ✅ プロンプトの簡潔化（API負荷軽減）
4. ✅ 履歴保存エラーの修正

### 期待される効果

- 500エラーの発生率が大幅に低下
- 様々な形式の画像に対応
- 履歴が正常に保存される

---

## 🚀 次のステップ

### 1. アプリを再起動

```bash
python app/main.py
```

### 2. 推奨画像でテスト

- サイズ: 1000x1500px以下
- 形式: JPGまたはPNG
- 背景: シンプル

### 3. ログを確認

```
Resized reference person image to: ...
★★★ Added reference person image: ... ★★★
[OK] Image generated successfully!
```

**これらのログが表示されれば成功です！** ✨

---

**修正完了。再テストをお願いします！**

