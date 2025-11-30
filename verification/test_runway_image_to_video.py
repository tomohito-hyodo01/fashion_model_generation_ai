#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Runway API (gen4_turbo) を使って
「女の子の画像1枚 → その子が歩いたりポーズを取る動画」
を生成するテストスクリプト（APIキーをハードコーディング版）。

使い方:
    python test_runway_image_to_video.py input.png --output output.mp4

前提:
    pip install runwayml requests
"""

import argparse
import base64
import mimetypes
import os
import sys
import requests
from runwayml import RunwayML, TaskFailedError  # 公式SDK 

# ─────────────────────────────────────────────
# ★ここに Runway の APIキーをベタ書きします★
# ─────────────────────────────────────────────
RUNWAY_API_SECRET = "key_baf79e014158bb01f984371a59735e7a6447b05d1111c097d3ec3e7edde7be3eb644172ffe96436df49ac3378d428088b77a2f2f169a3caa0f0364d4cc1b38f22"

def image_to_data_uri(image_path: str) -> str:
    """ローカル画像を Data URI (base64) に変換する。
    Runway は URL だけでなく Data URI も受け付ける。
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")
    
    # 拡張子から MIME タイプを判定（png/jpg/webp など）
    mime, _ = mimetypes.guess_type(image_path)
    if mime is None:
        mime = "image/png"  # 不明な場合はとりあえず PNG 扱い
    
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    
    data_uri = f"data:{mime};base64,{b64}"
    return data_uri

def generate_video(
    image_path: str,
    output_path: str,
    duration: int = 6,
    ratio: str = "1280:720",
    prompt_text: str | None = None,
    timeout: int = 600,
) -> None:
    """
    Runway の image_to_video を叩いて動画を生成し、MP4 を保存する。
    
    image_path : 入力画像（女の子の画像など）
    output_path : 出力するMP4ファイルパス
    duration : 秒数（プランにより上限あり）
    ratio : アスペクト比 (例: 1280:720 / 720:1280 / 960:960 など)
    prompt_text : 歩き・ポーズを指示する英語プロンプト
    timeout : タスク完了待ちの最大秒数
    """
    if not RUNWAY_API_SECRET or RUNWAY_API_SECRET == "YOUR_RUNWAY_API_KEY_HERE":
        raise RuntimeError(
            "RUNWAY_API_SECRET が設定されていません。\n"
            "このファイル先頭付近の RUNWAY_API_SECRET に、Runway の APIキーをベタ書きしてください。"
        )
    
    # 画像 → Data URI に変換（公式ドキュメントのサンプルと同じ方式）
    prompt_image = image_to_data_uri(image_path)
    
    # 歩き＋ポーズを意識したサンプルプロンプト
    if not prompt_text:
        prompt_text = (
            "A full-body cinematic shot of the same fashion model as in the input image, "
            "walking slowly toward the camera on a runway and then striking elegant fashion poses, "
            "smooth natural motion, professional modeling, high quality, 8-second clip."
        )
    
    print("=== Runway image_to_video テスト ===")
    print(f"入力画像 : {image_path}")
    print(f"出力動画 : {output_path}")
    print(f"model    : gen4_turbo")
    print(f"ratio    : {ratio}")
    print(f"duration : {duration} 秒")
    print(f"prompt   : {prompt_text}")
    print("====================================")
    
    # Runway クライアント初期化（api_key を直接指定）
    client = RunwayML(api_key=RUNWAY_API_SECRET)
    
    try:
        # 画像→動画タスクを作成し、完了まで待機
        # 公式クイックスタートの gen4_turbo 例をベースに image_to_video を使用。
        image_task = client.image_to_video.create(
            model="gen4_turbo",
            prompt_image=prompt_image,
            prompt_text=prompt_text,
            ratio=ratio,
            duration=duration,
        )
        
        task_output = image_task.wait_for_task_output(timeout=timeout)
        
    except TaskFailedError as e:
        print("❌ Runway のタスクが失敗しました。")
        print("task_details:", e.task_details)
        raise
    except Exception as e:
        print("❌ 予期しないエラー:", e)
        raise
    
    print("✅ タスク完了: status =", getattr(task_output, "status", "unknown"))
    
    # output[0] に動画URLが入っている想定（公式例と同じ仕様）
    video_url = None
    output_field = getattr(task_output, "output", None)
    if output_field and len(output_field) > 0:
        first = output_field[0]
        if isinstance(first, str):
            video_url = first
        elif isinstance(first, dict):
            video_url = first.get("url") or first.get("asset_url")
    
    if not video_url:
        print("⚠️ 動画URLが task_output.output から取得できませんでした。")
        print("task_output:", task_output)
        raise RuntimeError("動画URLが見つかりません。")
    
    print("動画URL:", video_url)
    
    # 動画をダウンロードして保存
    print("🎬 動画をダウンロード中...")
    resp = requests.get(video_url)
    resp.raise_for_status()
    
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)
    
    size_mb = len(resp.content) / (1024 * 1024)
    print(f"✅ 保存完了: {output_path} ({size_mb:.2f} MB)")

def main():
    parser = argparse.ArgumentParser(
        description="Runway gen4_turbo を使った image_to_video テストスクリプト"
    )
    parser.add_argument(
        "image",
        help="入力画像ファイルのパス（ファッションモデルの画像など。権利のある画像のみ使用してください）",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="runway_output.mp4",
        help="出力する動画ファイルパス (デフォルト: runway_output.mp4)",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=6,
        help="動画の秒数 (例: 3〜10 秒程度。プランにより上限あり)",
    )
    parser.add_argument(
        "--ratio",
        "-r",
        default="1280:720",
        help="動画のアスペクト比 (例: 1280:720 / 720:1280 / 960:960 など)",
    )
    parser.add_argument(
        "--prompt",
        "-p",
        default=None,
        help="英語のプロンプト（未指定なら「歩く＋ポーズ」のサンプルプロンプトを使用）",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="タスク完了を待つ最大秒数 (デフォルト: 600秒)",
    )
    
    args = parser.parse_args()
    
    try:
        generate_video(
            image_path=args.image,
            output_path=args.output,
            duration=args.duration,
            ratio=args.ratio,
            prompt_text=args.prompt,
            timeout=args.timeout,
        )
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    main()



