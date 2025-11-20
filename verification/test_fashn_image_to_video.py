#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FASHN image-to-video テスト用 CLI スクリプト

使い方例:
    python test_fashn_image_to_video.py input.jpg \
        --duration 5 \
        --resolution 1080p \
        --prompt "walking forward and changing pose" \
        --output model_walk.mp4
"""

import argparse
import base64
import mimetypes
import sys
import time
from pathlib import Path

import requests

# ==============================
# ★ ここに自分の FASHN APIキーをベタ書きしてください ★
# ==============================
API_KEY = "fa-uCRCpnOMl0uK-ylgH33BqyMDdtVyiEZ9SDRLo"

BASE_URL = "https://api.fashn.ai/v1"
RUN_ENDPOINT = f"{BASE_URL}/run"
STATUS_ENDPOINT_TEMPLATE = f"{BASE_URL}/status/{{prediction_id}}"

MODEL_NAME = "image-to-video"  # FASHN公式ドキュメント記載のモデル名


def encode_image_to_base64(image_path: Path) -> str:
    """画像ファイルを Base64(data URL 形式) に変換する。

    FASHN側は `data:image/xxx;base64,...` 形式のprefix付きBase64を要求します。
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


def create_image_to_video_prediction(
    image_data_url: str,
    duration: int = 5,
    resolution: str = "1080p",
    prompt: str | None = None,
) -> str:
    """image-to-video 予測ジョブを作成し、prediction_id を返す。"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    inputs: dict = {
        "image": image_data_url,
        "duration": duration,   # 5 or 10 seconds
        "resolution": resolution,  # 480p / 720p / 1080p
    }

    # motion ガイドの prompt は任意。
    if prompt:
        inputs["prompt"] = prompt

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
    """`/v1/status/{id}` をポーリングして、完了時には output URL のリストを返す。"""
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
                raise RuntimeError("status=completed ですが output が空です。レスポンス: " + str(data))
            return outputs

        if status == "failed":
            raise RuntimeError(f"予測が失敗しました: {error}")

        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise TimeoutError(f"予測がタイムアウトしました (>{timeout}秒)")

        # starting / in_queue / processing の間は待機して再ポーリング
        print(f"    状態: {status} ... {poll_interval}秒待機")
        time.sleep(poll_interval)


def download_video(video_url: str, output_path: Path) -> None:
    """生成された動画URLからMP4をダウンロードする。"""
    with requests.get(video_url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with output_path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="FASHN image-to-video テストプログラム（静止画→動画）"
    )
    parser.add_argument("image", help="入力画像ファイルパス（ファッションモデルの画像など）")
    parser.add_argument(
        "--duration",
        type=int,
        choices=[5, 10],
        default=10,
        help="動画の長さ（秒）。対応値: 5 or 10（デフォルト: 10）",
    )
    parser.add_argument(
        "--resolution",
        choices=["480p", "720p", "1080p"],
        default="1080p",
        help="動画解像度（デフォルト: 1080p）",
    )
    parser.add_argument(
        "--prompt",
        default="fashion model rotating 360 degrees and striking elegant poses from different angles, turning left and right, showing front, side and back views, professional runway modeling, smooth transitions between poses",
        help=(
            "任意の動きガイド（英語推奨）。"
            '例: "fashion model walking on runway and changing poses" '
            "※空文字の場合はFASHN側の自動モーションに任せます。"
        ),
    )
    parser.add_argument(
        "--output",
        default="fashn_output.mp4",
        help="保存する動画ファイル名（デフォルト: fashn_output.mp4）",
    )

    args = parser.parse_args()

    if API_KEY == "YOUR_FASHN_API_KEY_HERE":
        print(
            "まずソースコード内の API_KEY にあなたの FASHN APIキーを設定してください。",
            file=sys.stderr,
        )
        return 1

    image_path = Path(args.image)
    output_path = Path(args.output)

    try:
        print("=== FASHN image-to-video テスト ===")
        print(f"入力画像: {image_path}")
        print(f"出力動画: {output_path}")
        print(f"解像度: {args.resolution}")
        print(f"動画長: {args.duration}秒")
        print(f"プロンプト: {args.prompt or '(デフォルト自動モーション)'}")
        print("===================================")
        
        print("[1/4] 画像をBase64にエンコード中...")
        image_data_url = encode_image_to_base64(image_path)

        print("[2/4] image-to-video 予測ジョブを作成中...")
        prediction_id = create_image_to_video_prediction(
            image_data_url=image_data_url,
            duration=args.duration,
            resolution=args.resolution,
            prompt=args.prompt or None,
        )
        print(f"    prediction_id = {prediction_id}")

        print("[3/4] ステータスをポーリング中...")
        outputs = poll_prediction_status(prediction_id)
        video_url = outputs[0]
        print(f"    生成された動画URL: {video_url}")

        print(f"[4/4] 動画をダウンロード中: {output_path}")
        download_video(video_url, output_path)
        print("✅ 完了しました！")

        return 0

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

