#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FASHN Virtual Try-On v1.6 テスト用 CLI スクリプト

人物画像 + 服画像 → 着せ替え済み画像を生成します。

使い方例:
    python test_fashn_virtual_tryon.py person.jpg garment.png \
        --mode quality \
        --output-prefix tryon_result

出力例:
    tryon_result_0.png  がカレントディレクトリに保存されます
"""

import argparse
import base64
import mimetypes
import sys
import time
from pathlib import Path

import requests

# =========================================
# ★ ここに自分の FASHN APIキーをベタ書きしてください ★
# =========================================
API_KEY = "fa-uCRCpnOMl0uK-ylgH33BqyMDdtVyiEZ9SDRLo"

BASE_URL = "https://api.fashn.ai/v1"
RUN_ENDPOINT = f"{BASE_URL}/run"
STATUS_ENDPOINT_TEMPLATE = f"{BASE_URL}/status/{{prediction_id}}"

# Virtual Try-On v1.6 のモデル名（ドキュメント記載）
MODEL_NAME = "tryon-v1.6"


def encode_image_to_base64_data_url(image_path: Path) -> str:
    """
    画像ファイルを Base64(Data URL形式) に変換する。

    FASHNでは、Base64画像を渡す場合は
    `data:image/jpg;base64,<BASE64>` のような prefix が必須。
    """
    if not image_path.exists():
        raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")

    mime_type, _ = mimetypes.guess_type(str(image_path))
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError(f"画像ファイルではない可能性があります: {image_path}")

    with image_path.open("rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")

    data_url = f"data:{mime_type};base64,{b64}"
    return data_url


def create_tryon_prediction(
    model_image_data_url: str,
    garment_image_data_url: str,
    category: str = "auto",
    garment_photo_type: str = "auto",
    mode: str = "balanced",
    segmentation_free: bool = True,
    moderation_level: str = "permissive",
    num_samples: int = 1,
    output_format: str = "png",
    seed: int | None = None,
) -> str:
    """
    Virtual Try-On v1.6 の予測ジョブを作成し、prediction_id を返す。
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    inputs: dict = {
        "model_image": model_image_data_url,
        "garment_image": garment_image_data_url,
        "category": category,                   # 'auto' | 'tops' | 'bottoms' | 'one-pieces'
        "garment_photo_type": garment_photo_type,  # 'auto' | 'flat-lay' | 'model'
        "mode": mode,                           # 'performance' | 'balanced' | 'quality'
        "segmentation_free": segmentation_free, # bool
        "moderation_level": moderation_level,   # 'conservative' | 'permissive' | 'none'
        "num_samples": num_samples,             # 1–4
        "output_format": output_format,         # 'png' | 'jpeg'
    }

    if seed is not None:
        inputs["seed"] = seed  # 0〜2^32-1

    payload = {
        "model_name": MODEL_NAME,
        "inputs": inputs,
    }

    resp = requests.post(RUN_ENDPOINT, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    if data.get("error"):
        raise RuntimeError(f"FASHN API error: {data['error']}")

    prediction_id = data.get("id")
    if not prediction_id:
        raise RuntimeError(f"予測IDがレスポンスに含まれていません: {data}")

    return prediction_id


def poll_prediction_status(
    prediction_id: str,
    poll_interval: int = 5,
    timeout: int = 300,
) -> list[str]:
    """
    /v1/status/{id} をポーリングして、完了したら output(URL) のリストを返す。
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }
    status_url = STATUS_ENDPOINT_TEMPLATE.format(prediction_id=prediction_id)

    start_time = time.time()

    while True:
        resp = requests.get(status_url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        status = data.get("status")
        error = data.get("error")

        if status == "completed":
            outputs = data.get("output") or []
            if not outputs:
                raise RuntimeError(
                    "status=completed ですが output が空です。レスポンス: " + str(data)
                )
            return outputs

        if status == "failed":
            raise RuntimeError(f"予測が失敗しました: {error}")

        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise TimeoutError(f"予測がタイムアウトしました (>{timeout}秒)")

        # starting / in_queue / processing の間は待機
        print(f"    状態: {status} ... {poll_interval}秒待機")
        time.sleep(poll_interval)


def download_image(image_url: str, output_path: Path) -> None:
    """生成された画像URLからファイルをダウンロードする。"""
    with requests.get(image_url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with output_path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="FASHN Virtual Try-On v1.6 テストプログラム（人物＋服 → 着用画像）"
    )
    parser.add_argument("model_image", help="人物（モデル）の画像ファイルパス")
    parser.add_argument("garment_image", help="服（garment）の画像ファイルパス")

    parser.add_argument(
        "--category",
        choices=["auto", "tops", "bottoms", "one-pieces"],
        default="auto",
        help="服カテゴリ（デフォルト: auto）",
    )
    parser.add_argument(
        "--garment-photo-type",
        choices=["auto", "flat-lay", "model"],
        default="auto",
        help="服画像の種類: auto / flat-lay / model（デフォルト: auto）",
    )
    parser.add_argument(
        "--mode",
        choices=["performance", "balanced", "quality"],
        default="quality",
        help="処理モード: performance / balanced / quality（デフォルト: quality）",
    )
    parser.add_argument(
        "--moderation-level",
        choices=["conservative", "permissive", "none"],
        default="permissive",
        help="コンテンツモデレーションレベル（デフォルト: permissive）",
    )

    # segmentation_free を True/False 切り替え可能に
    parser.add_argument(
        "--segmentation-free",
        dest="segmentation_free",
        action="store_true",
        help="segmentation_free を有効にする（デフォルト）",
    )
    parser.add_argument(
        "--no-segmentation-free",
        dest="segmentation_free",
        action="store_false",
        help="segmentation_free を無効にする（元の服の除去が弱いときに試す）",
    )
    parser.set_defaults(segmentation_free=True)

    parser.add_argument(
        "--num-samples",
        type=int,
        default=1,
        help="一度に生成する画像枚数（1〜4, デフォルト: 1）",
    )
    parser.add_argument(
        "--output-format",
        choices=["png", "jpeg"],
        default="png",
        help="出力画像フォーマット（デフォルト: png）",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="乱数シード（同じ入力＋同じseedで再現性確保。未指定ならランダム）",
    )
    parser.add_argument(
        "--output-prefix",
        default="tryon_output",
        help="保存時のファイル名プレフィックス（デフォルト: tryon_output）",
    )

    args = parser.parse_args()

    if API_KEY == "YOUR_FASHN_API_KEY_HERE":
        print(
            "まずソースコード内の API_KEY にあなたの FASHN APIキーを設定してください。",
            file=sys.stderr,
        )
        return 1

    model_path = Path(args.model_image)
    garment_path = Path(args.garment_image)

    try:
        print("=== FASHN Virtual Try-On v1.6 テスト ===")
        print(f"人物画像: {model_path}")
        print(f"服画像: {garment_path}")
        print(f"カテゴリ: {args.category}")
        print(f"処理モード: {args.mode}")
        print(f"生成枚数: {args.num_samples}")
        print("=========================================")
        
        print("[1/4] モデル画像をBase64にエンコード中...")
        model_data_url = encode_image_to_base64_data_url(model_path)

        print("[2/4] 服画像をBase64にエンコード中...")
        garment_data_url = encode_image_to_base64_data_url(garment_path)

        print("[3/4] Virtual Try-On 予測ジョブを作成中...")
        prediction_id = create_tryon_prediction(
            model_image_data_url=model_data_url,
            garment_image_data_url=garment_data_url,
            category=args.category,
            garment_photo_type=args.garment_photo_type,
            mode=args.mode,
            segmentation_free=args.segmentation_free,
            moderation_level=args.moderation_level,
            num_samples=args.num_samples,
            output_format=args.output_format,
            seed=args.seed,
        )
        print(f"    prediction_id = {prediction_id}")

        print("[4/4] ステータスをポーリング中...")
        outputs = poll_prediction_status(prediction_id)
        print(f"    出力された画像URL数: {len(outputs)}")

        # 拡張子は output_format に合わせて決定
        ext = ".png" if args.output_format == "png" else ".jpg"

        for idx, url in enumerate(outputs):
            out_path = Path(f"{args.output_prefix}_{idx}{ext}")
            print(f"    画像 {idx}: {url}")
            print(f"    保存先: {out_path}")
            download_image(url, out_path)

        print("完了しました！")
        return 0

    except Exception as e:
        print(f"エラーが発生しました: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())



