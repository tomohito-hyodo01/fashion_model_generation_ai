"""
画像シーケンスから疑似動画を生成するテストコード

Stable Video APIが利用できない場合の代替案として、
複数の角度・ポーズの画像を連続生成してMP4動画を作成します。

使用方法:
    python verification/test_image_sequence_video.py

必要なパッケージ:
    pip install opencv-python
"""

import os
import sys
import time
from pathlib import Path
from typing import List
from PIL import Image
import numpy as np

# OpenCV のインポート（動画生成用）
try:
    import cv2
except ImportError:
    print("❌ OpenCVがインストールされていません")
    print("   以下のコマンドでインストールしてください：")
    print("   pip install opencv-python")
    sys.exit(1)

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def create_video_from_images(
    image_paths: List[str],
    output_path: str,
    fps: int = 24,
    duration_per_frame: float = 0.5
) -> bool:
    """
    画像リストから動画を生成
    
    Args:
        image_paths: 画像ファイルパスのリスト
        output_path: 出力動画のパス
        fps: フレームレート（1秒あたりのフレーム数）
        duration_per_frame: 1枚の画像を表示する時間（秒）
    
    Returns:
        成功した場合はTrue
    """
    if not image_paths:
        print("❌ 画像が指定されていません")
        return False
    
    print(f"\n🎬 動画生成中...")
    print(f"   入力画像数: {len(image_paths)}")
    print(f"   FPS: {fps}")
    print(f"   1枚あたりの表示時間: {duration_per_frame}秒")
    
    # 最初の画像から解像度を取得
    first_image = Image.open(image_paths[0])
    width, height = first_image.size
    
    print(f"   解像度: {width}x{height}")
    
    # VideoWriterの初期化
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height)
    )
    
    if not video_writer.isOpened():
        print("❌ VideoWriterの初期化に失敗しました")
        return False
    
    # 各画像をフレームとして追加
    frames_per_image = int(fps * duration_per_frame)
    
    for i, img_path in enumerate(image_paths):
        print(f"   処理中: {i+1}/{len(image_paths)} - {Path(img_path).name}")
        
        # 画像を読み込み
        img = Image.open(img_path)
        
        # サイズが異なる場合はリサイズ
        if img.size != (width, height):
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # PIL Image → NumPy配列 → OpenCV形式（BGR）
        img_array = np.array(img.convert('RGB'))
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # 同じフレームを複数回書き込み（duration_per_frame秒分）
        for _ in range(frames_per_image):
            video_writer.write(img_bgr)
    
    video_writer.release()
    
    # ファイルサイズを取得
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    total_duration = len(image_paths) * duration_per_frame
    
    print(f"\n✅ 動画を保存しました: {output_path}")
    print(f"   ファイルサイズ: {file_size_mb:.2f} MB")
    print(f"   総再生時間: {total_duration:.1f}秒")
    
    return True


def test_sequence_video():
    """
    既存の生成画像から疑似動画を作成するテスト
    """
    print("=" * 70)
    print("🎬 画像シーケンスから疑似動画を生成（代替案）")
    print("=" * 70)
    
    # 既存の画像ファイルを探す
    verification_dir = Path(__file__).parent
    
    # verificationディレクトリ内のPNG画像を取得
    image_files = sorted(verification_dir.glob("*.png"))
    
    # サンプル画像と出力ファイルは除外
    exclude_names = ["sample_tshirt.png", "output_sequence_video.png"]
    image_files = [
        f for f in image_files 
        if f.name not in exclude_names and not f.name.startswith("output")
    ]
    
    if not image_files:
        print("\n❌ 動画化する画像が見つかりません")
        print("   verificationディレクトリに画像を配置してください")
        return False
    
    print(f"\n📁 見つかった画像: {len(image_files)}枚")
    for img_file in image_files[:5]:  # 最初の5枚だけ表示
        print(f"   - {img_file.name}")
    if len(image_files) > 5:
        print(f"   ... 他 {len(image_files) - 5}枚")
    
    # 出力動画のパス
    output_video = verification_dir / "output_sequence_video.mp4"
    
    # 動画を生成
    success = create_video_from_images(
        image_paths=[str(f) for f in image_files],
        output_path=str(output_video),
        fps=24,
        duration_per_frame=0.5  # 各画像を0.5秒表示
    )
    
    if success:
        print("\n" + "=" * 70)
        print("✅ テスト成功！")
        print(f"   出力動画: {output_video}")
        print("\n💡 この方法は以下の場合に有効です：")
        print("   - 複数角度の画像を連続表示")
        print("   - ビフォー・アフターの比較動画")
        print("   - スライドショー形式の動画")
        print("=" * 70)
        return True
    else:
        print("\n" + "=" * 70)
        print("❌ テスト失敗")
        print("=" * 70)
        return False


def create_rotation_demo(
    input_image: str = "verification/sample_tshirt.png",
    output_video: str = "verification/rotation_demo.mp4",
    num_frames: int = 30
) -> bool:
    """
    1枚の画像を回転させて動画を作成するデモ
    
    Args:
        input_image: 入力画像
        output_video: 出力動画
        num_frames: フレーム数
    
    Returns:
        成功した場合はTrue
    """
    if not os.path.exists(input_image):
        print(f"❌ 入力画像が見つかりません: {input_image}")
        return False
    
    print(f"\n🔄 回転デモ動画を生成中...")
    print(f"   入力画像: {input_image}")
    print(f"   フレーム数: {num_frames}")
    
    # 画像を読み込み
    img = Image.open(input_image)
    width, height = img.size
    
    # VideoWriterの初期化
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(
        output_video,
        fourcc,
        24,  # 24 FPS
        (width, height)
    )
    
    # 各フレームで少しずつ回転
    for i in range(num_frames):
        angle = (360 / num_frames) * i
        
        # 画像を回転
        rotated = img.rotate(angle, expand=False)
        
        # PIL Image → NumPy → OpenCV
        img_array = np.array(rotated.convert('RGB'))
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        video_writer.write(img_bgr)
        
        if (i + 1) % 10 == 0:
            print(f"   進捗: {i+1}/{num_frames} フレーム")
    
    video_writer.release()
    
    file_size_mb = os.path.getsize(output_video) / (1024 * 1024)
    print(f"\n✅ 回転デモ動画を保存: {output_video}")
    print(f"   ファイルサイズ: {file_size_mb:.2f} MB")
    
    return True


if __name__ == "__main__":
    print("\n選択してください：")
    print("1. 既存画像から疑似動画を生成")
    print("2. 回転デモ動画を生成")
    
    choice = input("\n選択 (1 or 2): ").strip()
    
    if choice == "1":
        success = test_sequence_video()
    elif choice == "2":
        success = create_rotation_demo()
    else:
        print("❌ 無効な選択です")
        success = False
    
    sys.exit(0 if success else 1)


