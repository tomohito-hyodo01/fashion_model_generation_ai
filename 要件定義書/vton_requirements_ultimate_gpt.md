
# 衣類画像→モデル着用画像アプリ 要件定義書（最強版 / Python・Windowsデスクトップ）

> 目的：**衣類画像を忠実に着せたモデル画像**を、指定の人物属性で**1〜4枚**出力する高品質アプリを**短納期・低手戻り**で実装可能にする。  
> 本書は **Claude Code / Cursor** 等の生成AIコーディングツールへ**そのまま貼り付け**可能な粒度で記述。  
> ※ 利用APIは **OpenAI（DALL·E 3 / gpt-image-1）**、**Stability AI（Stable Diffusion系）**、**Google Imagen（Vertex/Gemini API）**。

---

## 1. ゴール / 非ゴール
- **ゴール**：投入衣類の**色・柄・形状・質感を改変せず**、指定モデル（年代/性別/地域テイスト/体型/ポーズ/背景）に**忠実に着せた画像**を生成。**出力枚数1〜4**も選択可。
- **非ゴール**：衣類の意匠をアレンジ/創作する機能、権利処理の自動化。

## 2. スコープ
- **OS**：Windows 10/11（x64）  
- **GUI**：Qt for Python（PySide6）
- **画像入出力**：入力 PNG/JPEG（推奨PNG透過）。出力 PNG/JPEG＋メタJSON（推奨PNG）。
- **配布**：PyInstaller による単一 EXE（オプション MSIX）。
- **API切替**：OpenAI / Stability / Vertex（アダプタパターン）。
- **ポリシー**：各社の生成/編集/透かし（SynthID）/安全性ガイドラインに準拠。

## 3. 主要ユースケース
1. 複数の衣類画像（上着/パンツ/Tシャツ/ワンピース/アクセ等）をD&Dまたは選択で投入。  
2. モデル属性（年代/性別/地域テイスト/体型/身長感/ポーズ）と背景を指定。  
3. 生成エンジン（OpenAI/Stability/Vertex）、画質/解像度/seed を選択。  
4. **出力枚数（1〜4）**を指定し生成。  
5. ギャラリーで並列プレビュー/拡大/差分ヒートマップ/指標スコア表示。  
6. 不合格時は自動リジェネ/パラメータ補正。保存/履歴/バッチ書き出し。

## 4. 機能要件

### 4.1 入力
- 画像：1〜N枚。カテゴリスロット（Top/Bottom/Outer/One-piece/Accessory）。
- バリデーション：最小辺≥512px、極端な圧縮/トリミングを警告、EXIF除去。
- 前処理（ローカル）：衣類領域セグメンテーション、マスク生成、色ヒスト/テクスチャKeypoint抽出、シルエット抽出。

### 4.2 モデル（人物）設定
- 年代：10/20/30/40/50+、性別：任意（非二元含む）、**地域テイスト**（アジア風/欧米風 等）。
- 体型/身長感/ポーズ：プリセット＋微調整。背景：白/透過/スタジオ/ロケ。

### 4.3 出力枚数（1〜4）— 共通IFとプロバイダ対応
- 共通IF：`generate(garments[], model_profile, controls, quality, num_outputs) -> List[Image], Meta`
- **OpenAI（DALL·E 3 / gpt-image-1）**：**DALL·E 3 は 1リクエスト=1枚**のため、並列/逐次で `num_outputs` 枚を取得（gpt-image-1は画像返却がBase64固定）。
- **Stability AI**：`samples = num_outputs`（1〜4）に対応。上限超/制約時は分割。
- **Google Imagen（Vertex/Gemini）**：`numberOfImages = num_outputs`（1〜4）。`aspectRatio`/`imageSize` も指定可。

### 4.4 忠実再現ロジック（最重要）
- **強制制約（プロンプト先頭に常付与）**：  
  `EXACT REPLICATION REQUIRED: Reproduce the clothing items PRECISELY as shown. NO modifications, NO artistic interpretation, NO style changes. Preserve colors (Hex/RAL), patterns, seams, silhouette, textures.`
- 自動検証：衣類領域の **SSIM / 色ヒスト相関 / 柄Keypoint一致 /（任意）LPIPS** を算出。
- 初期閾値（運用調整可）：SSIM≥0.85、色ヒスト相関≥0.90、Keypoint一致≥0.80。
- 不合格時自動リジェネ：
  - Stability：`strength`↓、`cfg_scale`↑、`negative_prompt`強化（alteration/restyle禁止）。
  - Vertex：参照重み↑・マスク厳格化・編集API/カスタマイズAPIで局所制御。
  - OpenAI：参照強調の固定句を追加・強化（“no redesign/no color shift …”）。
- **厳格モード**：衣類エッジ差分が閾値超過→即不合格。差分可視化（ヒートマップ）を提示。

### 4.5 プロンプト生成のコード化（取り込み）
- **ビルダー関数**を共通化し、衣類解析結果（色Hex/柄/形状/素材）とモデル属性から詳細プロンプト/ネガティブを自動組立：
```python
def build_faithful_prompt(clothing_items: list, model_attrs) -> dict:
    constraint = ("CRITICAL INSTRUCTION: Reproduce the described clothing items "
                  "EXACTLY without ANY modifications. Maintain precise colors, "
                  "patterns, seams, silhouette, and all design details.")
    model_desc = render_model_desc(model_attrs)  # 年代/性別/地域テイスト/体型/ポーズ
    clothing_desc = "Wearing: " + " ".join([c.analyzed_description for c in clothing_items])
    negative = "modified design, altered colors, different patterns, stylized, creative changes"
    return {
        "prompt": f"{constraint}\n\n{model_desc}\n\n{clothing_desc}\n\nProfessional studio lighting, neutral background.",
        "negative_prompt": negative
    }
```

### 4.6 UI/UX（取り込み＋拡張）
- **メインレイアウト（ASCIIワイヤー）**
```
┌─────────────────────────────────────────────────────────┐
│  Virtual Fashion Try-On                    [_][□][X]    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌────────────────────────────┐   │
│  │  画像アップロード  │  │  モデル属性選択            │   │
│  │  [+ 追加]       │  │  性別/年代/地域/体型/ポーズ  │   │
│  │  [上着][パンツ] │  └──────────┬─────────┘   │
│  └─────────────────┘             │                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  生成AI選択: ○DALL·E3  ○Stable  ○Imagen         │  │
│  │  品質:[標準v] サイズ:[1024x1024v] **枚数:[1..4]** │  │
│  │                        [生成開始]                 │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  生成結果（サムネ x4）  [保存] [履歴]             │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```
- 操作性：D&D、キーボードショートカット、ストリーム表示（生成完了順）。
- エラーUX：レート制限/ネットワーク/ポリシー違反を**原因別**に整形表示（再試行提案含む）。
- カラースキーム例：Dark Blue/Green/Light Gray（任意）。

### 4.7 出力
- 画像（PNG/JPEG）＋ **メタJSON**（プロバイダ/パラメータ/seed/忠実度スコア/リトライ履歴）。
- 再現性：プロバイダが対応する場合は **seed固定**で再生成一致を担保。

## 5. 非機能要件（取り込み＋数値化）
- **応答性**：UI基本操作の即応（100ms以内）。
- **生成レイテンシ**：API依存（10〜60秒目安）。進捗/部分結果をストリーミング表示。
- **並列度**：OpenAIは**並列/逐次**で複数枚生成（RPM/コスト/同時セッションを設定可能）。
- **リトライ**：ネットワーク/429等は指数バックオフ、**最大3回**。部分成功を許容。
- **ログ**：要約ログ（PII/画像の永続保存は既定OFF）。
- **セキュリティ**：
  - **APIキー保護はDPAPI（CryptProtectData）を第一候補**。Fernetは移植用の第2候補（鍵は同梱禁止）。
  - 交通路はHTTPS必須。設定ファイルは `.env`（暗号化/非同梱）。
- **法令/ポリシー**：各社の生成規約、透かし（SynthID）への対応、実在人物・商標・著作物の扱いを明示。

## 6. アーキテクチャ / ディレクトリ
```
app/
  main.py
  app.py
  ui/
    main_window.py
    widgets/
      garment_slot.py
      gallery_view.py
      metrics_panel.py
  core/
    adapters/
      provider_base.py
      openai_adapter.py
      stability_adapter.py
      vertex_adapter.py
    vton/
      segment.py
      mask_utils.py
      fidelity_check.py
      retry_policy.py
    pipeline/
      generate_service.py
      postprocess.py
      storage.py
    config/
      settings.py
      schema.py
  assets/
    icons/
  tests/
    test_adapters.py
    test_fidelity.py
    test_ui_smoke.py
  scripts/
    pack_win.ps1         # PyInstaller / 署名 / MSIX
  requirements.txt
  pyproject.toml
  .env.example
```

### 6.1 主要クラス
- `ProviderBase`: `prepare()`, `generate()`, `edit()`, `supports_seed()`, `supports_multi`
- `OpenAIAdapter / StabilityAdapter / VertexAdapter`
- `GenerateService`: 前処理→生成→**多枚数制御**→忠実度検証→再生成
- `FidelityChecker`: SSIM/LPIPS/色ヒスト/Keypoint
- `Storage`: 画像/メタ保存、再現用バンドル生成

### 6.2 フロー
```mermaid
flowchart LR
  A[衣類画像の投入] --> B[前処理(セグメント/マスク/特徴抽出)]
  B --> C[プロバイダ選択/パラメータ構築/出力枚数]
  C --> D[生成API呼び出し(必要に応じ並列バッチ)]
  D --> E[忠実度検証(SSIM/LPIPS/色/柄)]
  E -- 合格 --> F[保存(画像+メタ)/ギャラリー]
  E -- 不合格 --> C2[パラメータ補正&自動リジェネ]
  C2 --> D
```

## 7. プロバイダ別 実装指針（要点）
- **OpenAI（DALL·E 3 / gpt-image-1）**  
  - `images/generations` を使用。**DALL·E 3は `n=1` 固定**、複数枚は並列化。`gpt-image-1` はBase64返却。
  - 参照画像強調の固定句と negative を標準化。編集/マスク編集も想定。
- **Stability AI（Stable Diffusion系）**  
  - `image-to-image`：`strength` を低め（例0.2–0.35）、`cfg_scale` 高め。`samples=1..4`。
  - negative に *alteration/restyle* 禁止句を入れて忠実性を強化。
- **Google Imagen（Vertex/Gemini）**  
  - `numberOfImages=1..4`、`aspectRatio`、`imageSize`。編集API/カスタマイズAPI/参照画像活用。SynthIDの扱いをREADMEに記載。

## 8. 受け入れ基準（品質ゲート）
- **忠実度**：主要衣類領域で SSIM≥0.85、色ヒスト相関≥0.90、Keypoint一致≥0.80 を同時満たす。  
- **枚数**：1/2/3/4 の各パターンで、UIと保存・メタJSON・再現（seed）を含めて動作。  
- **失敗時の回復**：429/ネットワーク断で自動リトライ（最大3回）し、部分成功を表示。  
- **配布**：PyInstaller で `--onefile --noconsole` 成果物を作成し、クリーン環境で起動確認。

## 9. セキュリティ実装（例）
- **DPAPI（CryptProtectData/CryptUnprotectData）**で APIキーを**ユーザー/マシンにバインド**して暗号化保存。  
- Fernet 併用時は**鍵をアプリに同梱しない**（OS外出し/配布時はKMS等を使用）。

## 10. テスト計画
- **単体**：アダプタAPIモック、`FidelityChecker` の閾値テスト、リトライ/バックオフ。  
- **結合**：同一入力→3プロバイダ比較、**出力1〜4枚**の連続実行、忠実性リジェネが作動。  
- **UIスモーク**：D&D、枚数セレクタ、進捗/ストリーム表示、差分ヒートマップ、保存。  
- **配布テスト**：空のWindows VMで EXE 起動・API鍵投入・生成完走。

## 11. 納品物チェックリスト（取り込み）
- ソース一式 / 単体・結合テスト / **日本語・英語README** / .env.example / ビルドスクリプト。  
- 運用Runbook（レート制限/障害復旧手順/鍵ローテーション）。  
- 受け入れレポート（各指標の計測結果 / 1〜4枚の動作証跡 / スクリーンショット）。

## 12. 参考（開発者向け・リンク）
- OpenAI 画像生成（gpt-image-1 / Images API）: https://platform.openai.com/docs/guides/image-generation  
- Azure OpenAI（How to use image generation models）: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/dall-e  
- Stability AI API（image-to-image / params）: https://platform.stability.ai/docs/api-reference  
- Vertex/Gemini API（Imagen, numberOfImages=1..4）: https://ai.google.dev/gemini-api/docs/imagen  
- DPAPI（CryptProtectData / CryptUnprotectData）: https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata  
- PyInstaller: https://www.pyinstaller.org/ / https://pyinstaller.org/en/stable/usage.html  
- PySide6（QtWidgets）: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/index.html

---

## 付録A：多枚数対応・擬似コード
```python
class GenerateService:
    def __init__(self, adapter, fidelity_checker, retry_policy, max_parallel=4):
        self.adapter = adapter
        self.fidelity = fidelity_checker
        self.retry = retry_policy
        self.max_parallel = max_parallel

    def run(self, garments, profile, controls, quality, num_outputs):
        assert 1 <= num_outputs <= 4
        if getattr(self.adapter, "supports_multi", False):
            imgs, meta = self.adapter.generate(garments, profile, controls, quality, num_outputs)
            return self._post_check(imgs, meta)
        else:
            imgs, metas = [], []
            for i in range(num_outputs):
                img, meta = self.adapter.generate(garments, profile, controls, quality, 1)
                imgs.append(img); metas.append(meta)
            return self._post_check(imgs, {"partials": metas})

    def _post_check(self, imgs, meta):
        passed = []
        for img in imgs:
            score = self.fidelity.evaluate(img)
            if score.pass_all():
                passed.append((img, score.to_dict()))
            else:
                # TODO: self.retry.tune(...) で補正→再生成
                pass
        if not passed:
            raise ValueError("Fidelity not satisfied for all outputs")
        return [x[0] for x in passed], meta
```

## 付録B：設定とビルドの約束事
- `.env` に API キー類（OpenAI/Stability/Google）。
- `scripts/pack_win.ps1` で `pyinstaller --onefile --noconsole`、アイコン/署名/MSIX対応。
- APIキーは**DPAPI**で暗号化保存。移植パス用に Fernet 実装をオプション提供（鍵管理は別配布）。
