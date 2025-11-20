#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Luma Dream Machine (Ray 2) を使って
「1枚のファッションモデル画像 → その人が歩いたりポーズを取る動画」
を生成するテスト用CLIスクリプトです。

使い方:
    python test_luma_image_to_video.py <image_url> [output.mp4] [prompt]

例:
    python test_luma_image_to_video.py \
        https://example.com/model.png \
        model_walk_pose.mp4

前提:
    pip install lumaai requests
"""

import sys
import time
import pathlib
import requests
from lumaai import LumaAI

# ========= ここに Luma の APIキーを直書き =========
API_KEY = "luma-d228af7b-ae8a-4d70-9a37-b1b455abc0c9-3e45f46f-a400-4bc5-9027-3a11362fd661"
# ==============================================

def main():
    if len(sys.argv) < 2:
        print("使い方: python test_luma_image_to_video.py <image_url> [output.mp4] [prompt]")
        sys.exit(1)
    
    image_url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) >= 3 else "luma_output.mp4"
    
    # Lumaは英語プロンプトの方が安定しやすいのでデフォルトは英語。
    # 必要に応じて第3引数で差し替え可能です。
    default_prompt = (
        "Professional fashion model walking forward on a runway with confident strides, "
        "then stopping to strike elegant fashion poses, "
        "full body shot, smooth natural motion, high fashion photography style, camera tracking shot"
    )
    prompt = sys.argv[3] if len(sys.argv) >= 4 else default_prompt
    
    if not API_KEY or API_KEY == "luma_xxxxxxxxxxxxxxxxxxxxxxxxx":
        print("エラー: API_KEY が未設定です。コード内の API_KEY を自分のキーに書き換えてください。")
        sys.exit(1)
    
    # クライアント初期化（auth_token 直接指定）
    client = LumaAI(auth_token=API_KEY)
    
    print("=== Luma Dream Machine: Image to Video (Ray 2) テスト ===")
    print(f"画像URL:      {image_url}")
    print(f"出力ファイル: {output_path}")
    print(f"プロンプト:   {prompt}")
    print("動画生成ジョブを作成中...")
    
    try:
        # 公式Pythonドキュメントの Ray 2 Image to Video サンプルをベースに、
        # model='ray-2' + keyframes.frame0.type='image' を指定しています。
        generation = client.generations.create(
            prompt=prompt,
            model="ray-2",
            keyframes={
                "frame0": {
                    "type": "image",
                    "url": image_url,  # 公開アクセス可能な画像URL
                }
            },
            # 必要に応じてオプション:
            # resolution="720p",    # 540p / 720p / 1080 / 4k
            # duration="5s",        # "5s", "9s" など
            # aspect_ratio="16:9",
            # loop=False,
        )
        
        print(f"生成ID: {generation.id}")
        print("状態をポーリングして完了を待ちます...")
        
        # ---- 状態ポーリング ----
        completed = False
        while not completed:
            generation = client.generations.get(id=generation.id)
            
            if generation.state == "completed":
                completed = True
                print("状態: completed ✅")
            elif generation.state == "failed":
                print("状態: failed ❌")
                print(f"failure_reason: {generation.failure_reason}")
                sys.exit(1)
            else:
                print(f"状態: {generation.state} ... 3秒待機")
                time.sleep(3)
        
        # ---- 動画URL取得 ----
        video_url = getattr(generation.assets, "video", None)
        if not video_url:
            print("エラー: generation.assets.video が見つかりません。レスポンス形式が変わっている可能性があります。")
            print("レスポンス:", generation)
            sys.exit(1)
        
        print(f"動画URL: {video_url}")
        print("動画をダウンロード中...")
        
        # ---- 動画ダウンロード ----
        response = requests.get(video_url, stream=True)
        if response.status_code != 200:
            print(f"動画ダウンロード失敗: HTTP {response.status_code}")
            sys.exit(1)
        
        out_path = pathlib.Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        with out_path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"✅ 完了: {out_path} に保存しました。")
    
    except Exception as e:
        print("エラーが発生しました:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()


