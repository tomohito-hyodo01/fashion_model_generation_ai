# 参考人物機能 - 技術的制約と解決策

**作成日**: 2025年11月15日

---

## ❌ 現状の技術的制約

### Gemini 2.5 Flash Imageの制約

**できること**:
- ✅ 複数の画像を見て新しい画像を生成
- ✅ 画像を「参考」にして生成

**できないこと**:
- ❌ 既存画像の「一部だけ」を変更
- ❌ 人物のアイデンティティを100%保持
- ❌ 画像編集・インペインティング

### 要望と技術のギャップ

**ユーザー要望**:
```
参考人物画像の「服以外」はそのまま利用
服だけを変更
```

**現在のGemini実装**:
```
参考人物を「参考」にして新しい画像を生成
→ 服以外も変わってしまう ❌
```

---

## ✅ 解決策の提案

### 方法1: セグメンテーション + 合成（推奨）

**アプローチ**:
```
1. 参考人物画像から「人物」だけを切り抜き（セグメンテーション）
2. 服の部分を指定の服に置き換え
3. 元の背景と合成
```

**実装手順**:
- rembgまたはmediapipeで人物セグメンテーション
- OpenCVで服の領域を検出
- 新しい服を合成

**メリット**:
- ✅ 顔・体型を100%保持
- ✅ 追加APIキー不要

**デメリット**:
- 実装が複雑
- 自然な合成が難しい

---

### 方法2: Stability AI Inpainting API（最も確実）

**アプローチ**:
```
Stability AIのInpainting APIを使用
- 参考人物画像をベース
- 服の領域をマスクで指定
- その部分だけを新しい服で塗り替え
```

**実装例**:
```python
result = stability_inpainting(
    image=参考人物画像,
    mask=服の領域マスク,
    prompt="wearing red jacket from reference image"
)
```

**メリット**:
- ✅ 顔・体型を100%保持
- ✅ 高品質な合成
- ✅ 自然な仕上がり

**デメリット**:
- 追加APIキー必要（Stability AI）
- マスク生成が必要

---

### 方法3: プロンプトの極限まで強化

**最後の手段として、プロンプトをさらに強化**:

```
"This is an IMAGE EDITING task, not image generation.
INPUT: Person image (image 1) + Clothing image (image 2)
OUTPUT: Image 1 with ONLY the clothes changed to image 2

STRICT RULES:
- Copy image 1's person pixel-by-pixel for face/hair/body
- Replace ONLY clothing area with image 2's clothing
- Everything else stays EXACTLY as in image 1"
```

**期待される効果**:
- 類似度が現在の20% → 70-80%に向上（希望的観測）
- しかし100%保持は困難

---

## 🎯 推奨される実装順序

### Phase 5.1: Stability AI Inpainting実装（推奨）

```python
class StabilityInpaintingAdapter:
    def inpaint_clothing(
        self,
        person_image: Image.Image,
        clothing_image: Image.Image,
        mask: Image.Image
    ) -> Image.Image:
        """
        参考人物の服だけを変更
        
        Args:
            person_image: 参考人物画像（ベース）
            clothing_image: 新しい服の画像
            mask: 服の領域マスク（白=変更、黒=保持）
        
        Returns:
            服だけが変更された画像
        """
        # Stability AI Inpainting APIを呼び出し
        ...
```

**所要時間**: 約2-3時間

---

### Phase 5.2: セグメンテーション + 合成（代替案）

```python
class ImageCompositor:
    def replace_clothing(
        self,
        person_image: Image.Image,
        generated_clothing_image: Image.Image
    ) -> Image.Image:
        """
        セグメンテーションと合成による服の置き換え
        """
        # 1. 人物セグメンテーション
        person_mask = self.segment_person(person_image)
        
        # 2. 服の領域を検出
        clothing_mask = self.detect_clothing_area(person_image)
        
        # 3. 新しい服を生成（Gemini）
        new_clothing = gemini.generate(clothing_image)
        
        # 4. 合成
        result = self.composite(person_image, new_clothing, clothing_mask)
        
        return result
```

**所要時間**: 約3-4時間

---

## 📊 各手法の比較

| 手法 | 顔保持 | 実装難易度 | 追加API | 推奨度 |
|------|--------|----------|---------|--------|
| **現在のGemini** | 20% | - | 不要 | ⚠️ |
| **プロンプト強化** | 70%? | 低 | 不要 | 🟡 |
| **Stability Inpainting** | 100% | 中 | 必要 | ✅✅✅ |
| **セグメンテーション合成** | 100% | 高 | 不要 | 🟡 |

---

## 💡 即座に試せる改善

### 最強プロンプトの実装

現在のプロンプトをさらに強化して、もう一度試してみます。

```python
prompt_text = (
    f"IMPORTANT: This is an IMAGE EDITING task.\n"
    f"\n"
    f"STEP 1: Look at IMAGE 1 carefully.\n"
    f"- This shows a SPECIFIC PERSON with unique face, hair, and body.\n"
    f"- Memorize their face, hair style, hair color, skin tone, body proportions.\n"
    f"\n"
    f"STEP 2: Look at IMAGE 2.\n"
    f"- This shows CLOTHING ITEMS only.\n"
    f"\n"
    f"STEP 3: Your task is to EDIT image 1, not create a new person.\n"
    f"- Take the EXACT person from image 1\n"
    f"- Change ONLY their clothing to match image 2\n"
    f"- Keep EVERYTHING ELSE the same: face, hair, skin, body\n"
    f"\n"
    f"DO NOT create a new person.\n"
    f"DO NOT change the face.\n"
    f"DO NOT change the hair.\n"
    f"ONLY change the clothes.\n"
    f"\n"
    f"Output: The person from image 1 wearing clothes from image 2.\n"
)
```

---

## 🚀 次のステップ

### オプションA: 最強プロンプトを試す（即座）

今すぐ実装可能。効果は限定的かもしれないが、改善の可能性あり。

### オプションB: Stability AI Inpainting実装（確実）

2-3時間の実装時間が必要だが、確実に顔・体型を保持できる。

### オプションC: 機能の位置づけ変更

「参考人物に似たモデルを生成」として説明し、完全保持は求めない。

---

**どの方向性で進めますか？**

1. まず最強プロンプトを試す
2. Stability AI Inpainting実装に進む
3. 機能の説明を変更する

ご指示をお願いします。

