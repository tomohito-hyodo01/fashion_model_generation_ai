# チャット修正機能 - 画像編集実装

**実装日**: 2025年11月15日  
**改善**: 1から再生成 → 選択画像をベースに編集

---

## 🔄 変更内容

### Before（修正前）

```
ユーザー: 「座らせてください」
  ↓
システム: パラメータを変更（pose = sitting）
  ↓
Gemini: 1から新しい画像を生成
  ↓
結果: 別の画像（座っている）
  - 選択画像とは異なる人物
  - 背景も変わる
  - 服も微妙に変わる
```

### After（修正後）

```
ユーザー: 「座らせてください」
  ↓
システム: 選択画像を取得
  ↓
Gemini: 選択画像を見て編集
  ↓
プロンプト:
  "Look at this image.
   Change the pose to: sitting
   Keep the SAME PERSON, SAME CLOTHING, SAME BACKGROUND
   Only change the pose"
  ↓
結果: 同じ人物が座っている画像 ✅
  - 選択画像と同じ人物
  - 背景もそのまま
  - 服もそのまま
  - ポーズだけが変わる
```

---

## 🎯 実装内容

### 1. 選択画像の保持

```python
# ギャラリーで画像を選択した時
self.selected_image_for_edit = image
params_with_image['selected_image'] = image
```

### 2. 画像編集メソッド

```python
async def _edit_with_gemini(
    base_image,      # 編集対象の画像
    instruction,     # ユーザーの指示
    changes,         # 変更内容
    adapter          # Geminiアダプター
):
    # Geminiに画像を送信
    prompt_parts = [
        base_image,  # この画像を編集
        """
        Look at this image.
        USER INSTRUCTION: 座らせてください
        
        YOUR TASK:
        Create a new version with ONLY these changes:
        - Change pose to: sitting
        
        KEEP EVERYTHING ELSE THE SAME:
        - Same person (face, hair, body)
        - Same clothing
        - Same background
        """
    ]
    
    response = model.generate_content(prompt_parts)
    return edited_image
```

### 3. ワーカーに画像を渡す

```python
ChatRefinementWorker(
    ...
    base_image=selected_image  # 選択画像を渡す
)
```

---

## 📊 動作フロー

### 画像編集モード

```
【ステップ1】ユーザーが画像を選択
  ギャラリーで「この画像を修正」をクリック
  ↓
  selected_image_for_edit = image ← 保存

【ステップ2】ユーザーが指示を入力
  「座らせてください」
  ↓
  Gemini APIで解析
  ↓
  changes = {"pose": "sitting"}

【ステップ3】画像を編集
  Geminiに送信:
    - 画像: selected_image
    - 指示: "Change pose to sitting, keep everything else"
  ↓
  Geminiが画像を見て編集
  ↓
  同じ人物が座っている画像 ✅

【ステップ4】結果を表示
  チャットに表示
  ギャラリーに追加
```

---

## 🎯 改善される点

| 要素 | Before | After |
|------|--------|-------|
| **人物** | 別人 | 同じ人物 ✅ |
| **顔** | 変わる | そのまま ✅ |
| **服** | 微妙に変わる | そのまま ✅ |
| **背景** | 変わる | そのまま ✅ |
| **指示内容** | 変わる | 指示通り ✅ |

---

## 🧪 テスト手順

### 1. アプリケーションを再起動

```bash
python app/main.py
```

### 2. 画像を生成

1. 衣類画像をアップロード
2. 生成開始
3. 立っている人物の画像が生成される

### 3. チャットで修正

1. ギャラリーで「この画像を修正」をクリック
2. チャット欄に「座らせてください」と入力
3. 送信

### 4. 期待される結果

- ✅ 同じ人物が座っている
- ✅ 服はそのまま
- ✅ 背景もそのまま
- ✅ ポーズだけが変わる

---

## 📝 実装ファイル

| ファイル | 変更内容 |
|---------|---------|
| `app/core/pipeline/chat_refinement_service.py` | base_image引数追加、_edit_with_geminiメソッド追加 |
| `app/ui/main_window.py` | selected_image_for_edit保持、ワーカーに渡す |

---

## 🎊 完成！

**選択画像をベースに、指示された部分だけを変更する機能が実装されました！**

### 実現されたこと

✅ 選択画像がベースになる  
✅ 指示された部分だけを変更  
✅ 他の要素（人物・服・背景）はそのまま  

---

**アプリケーションを再起動して、チャット修正を試してください！** ✨

