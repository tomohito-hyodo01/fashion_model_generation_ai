"""
1枚の画像から動くアニメーション動画を生成

Ken Burns効果（ズーム・パン）や3D回転効果を使用して、
静止画から動きのある動画を生成します。

使用方法:
    python verification/test_animated_video.py

必要なパッケージ:
    pip install opencv-python numpy pillow
"""

import os
import sys
import numpy as np
from pathlib import Path
from PIL import Image
import math

try:
    import cv2
except ImportError:
    print("[ERROR] OpenCVがインストールされていません")
    print("   以下のコマンドでインストールしてください：")
    print("   pip install opencv-python")
    sys.exit(1)

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def create_ken_burns_video(
    image_path: str,
    output_path: str,
    duration: float = 3.0,
    fps: int = 30,
    effect: str = "zoom_in"
) -> bool:
    """
    Ken Burns効果で動画を生成
    
    Args:
        image_path: 入力画像のパス
        output_path: 出力動画のパス
        duration: 動画の長さ（秒）
        fps: フレームレート
        effect: エフェクトの種類
            - "zoom_in": ズームイン
            - "zoom_out": ズームアウト
            - "pan_right": 右にパン
            - "pan_left": 左にパン
            - "zoom_pan": ズーム+パン
    
    Returns:
        成功した場合はTrue
    """
    if not os.path.exists(image_path):
        print(f"[ERROR] 入力画像が見つかりません: {image_path}")
        return False
    
    print(f"\n[Ken Burns効果] 動画生成中...")
    print(f"   入力画像: {image_path}")
    print(f"   エフェクト: {effect}")
    print(f"   長さ: {duration}秒")
    print(f"   FPS: {fps}")
    
    # 画像を読み込み
    img = cv2.imread(image_path)
    if img is None:
        print(f"[ERROR] 画像の読み込みに失敗: {image_path}")
        return False
    
    height, width = img.shape[:2]
    total_frames = int(duration * fps)
    
    print(f"   解像度: {width}x{height}")
    print(f"   総フレーム数: {total_frames}")
    
    # VideoWriterの初期化
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not video_writer.isOpened():
        print("[ERROR] VideoWriterの初期化に失敗")
        return False
    
    # エフェクトに応じてフレームを生成
    for i in range(total_frames):
        progress = i / total_frames
        
        if effect == "zoom_in":
            # ズームイン: 徐々に拡大
            scale = 1.0 + (0.3 * progress)  # 1.0 → 1.3倍
            frame = zoom_image(img, scale)
            
        elif effect == "zoom_out":
            # ズームアウト: 徐々に縮小
            scale = 1.3 - (0.3 * progress)  # 1.3 → 1.0倍
            frame = zoom_image(img, scale)
            
        elif effect == "pan_right":
            # 右にパン
            offset_x = int(width * 0.2 * progress)
            frame = pan_image(img, offset_x, 0)
            
        elif effect == "pan_left":
            # 左にパン
            offset_x = -int(width * 0.2 * progress)
            frame = pan_image(img, offset_x, 0)
            
        elif effect == "zoom_pan":
            # ズーム+パン
            scale = 1.0 + (0.2 * progress)
            offset_x = int(width * 0.1 * progress)
            offset_y = int(height * 0.1 * progress)
            frame = zoom_image(img, scale)
            frame = pan_image(frame, offset_x, offset_y)
        
        else:
            frame = img.copy()
        
        video_writer.write(frame)
        
        if (i + 1) % 30 == 0:
            print(f"   進捗: {i+1}/{total_frames} フレーム")
    
    video_writer.release()
    
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n[OK] 動画を保存しました: {output_path}")
    print(f"   ファイルサイズ: {file_size_mb:.2f} MB")
    
    return True


def zoom_image(img: np.ndarray, scale: float) -> np.ndarray:
    """画像をズーム"""
    height, width = img.shape[:2]
    
    # 新しいサイズを計算
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # リサイズ
    resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    
    # 中央をクロップ
    start_x = (new_width - width) // 2
    start_y = (new_height - height) // 2
    
    if scale >= 1.0:
        # ズームイン: 中央部分を切り取り
        cropped = resized[start_y:start_y+height, start_x:start_x+width]
    else:
        # ズームアウト: 余白を追加
        cropped = np.zeros_like(img)
        y_offset = (height - new_height) // 2
        x_offset = (width - new_width) // 2
        cropped[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized
    
    return cropped


def pan_image(img: np.ndarray, offset_x: int, offset_y: int) -> np.ndarray:
    """画像をパン（移動）"""
    height, width = img.shape[:2]
    
    # 変換マトリックス
    M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
    
    # アフィン変換
    panned = cv2.warpAffine(img, M, (width, height), borderMode=cv2.BORDER_REPLICATE)
    
    return panned


def create_3d_rotation_video(
    image_path: str,
    output_path: str,
    duration: float = 3.0,
    fps: int = 30,
    rotation_axis: str = "y"
) -> bool:
    """
    3D回転効果で動画を生成
    
    Args:
        image_path: 入力画像のパス
        output_path: 出力動画のパス
        duration: 動画の長さ（秒）
        fps: フレームレート
        rotation_axis: 回転軸（"x", "y", "z"）
    
    Returns:
        成功した場合はTrue
    """
    if not os.path.exists(image_path):
        print(f"[ERROR] 入力画像が見つかりません: {image_path}")
        return False
    
    print(f"\n[3D回転効果] 動画生成中...")
    print(f"   入力画像: {image_path}")
    print(f"   回転軸: {rotation_axis}")
    print(f"   長さ: {duration}秒")
    
    # 画像を読み込み
    img = cv2.imread(image_path)
    if img is None:
        print(f"[ERROR] 画像の読み込みに失敗: {image_path}")
        return False
    
    height, width = img.shape[:2]
    total_frames = int(duration * fps)
    
    # VideoWriterの初期化
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not video_writer.isOpened():
        print("[ERROR] VideoWriterの初期化に失敗")
        return False
    
    # 3D回転のための準備
    center_x, center_y = width // 2, height // 2
    max_angle = 15  # 最大回転角度（度）
    
    for i in range(total_frames):
        progress = i / total_frames
        
        # 往復する回転（0° → max_angle → 0° → -max_angle → 0°）
        angle_progress = math.sin(progress * math.pi * 2) * max_angle
        
        if rotation_axis == "y":
            # Y軸回転（左右に傾ける）
            frame = rotate_3d_y(img, angle_progress, center_x, center_y)
        elif rotation_axis == "x":
            # X軸回転（上下に傾ける）
            frame = rotate_3d_x(img, angle_progress, center_x, center_y)
        else:
            # Z軸回転（平面回転）
            M = cv2.getRotationMatrix2D((center_x, center_y), angle_progress, 1.0)
            frame = cv2.warpAffine(img, M, (width, height))
        
        video_writer.write(frame)
        
        if (i + 1) % 30 == 0:
            print(f"   進捗: {i+1}/{total_frames} フレーム")
    
    video_writer.release()
    
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n[OK] 動画を保存しました: {output_path}")
    print(f"   ファイルサイズ: {file_size_mb:.2f} MB")
    
    return True


def rotate_3d_y(img: np.ndarray, angle: float, center_x: int, center_y: int) -> np.ndarray:
    """Y軸周りの3D回転"""
    height, width = img.shape[:2]
    
    # ラジアンに変換
    theta = np.radians(angle)
    
    # 透視変換行列を計算
    # Y軸回転の簡易版
    focal_length = width
    distance = focal_length
    
    # 変換行列
    src_points = np.float32([
        [0, 0],
        [width, 0],
        [0, height],
        [width, height]
    ])
    
    # Y軸回転後の座標
    offset = int(np.sin(theta) * width * 0.1)
    dst_points = np.float32([
        [offset, 0],
        [width - offset, 0],
        [offset, height],
        [width - offset, height]
    ])
    
    M = cv2.getPerspectiveTransform(src_points, dst_points)
    rotated = cv2.warpPerspective(img, M, (width, height), borderMode=cv2.BORDER_REPLICATE)
    
    return rotated


def rotate_3d_x(img: np.ndarray, angle: float, center_x: int, center_y: int) -> np.ndarray:
    """X軸周りの3D回転"""
    height, width = img.shape[:2]
    
    # ラジアンに変換
    theta = np.radians(angle)
    
    # 変換行列
    src_points = np.float32([
        [0, 0],
        [width, 0],
        [0, height],
        [width, height]
    ])
    
    # X軸回転後の座標
    offset = int(np.sin(theta) * height * 0.1)
    dst_points = np.float32([
        [0, offset],
        [width, offset],
        [0, height - offset],
        [width, height - offset]
    ])
    
    M = cv2.getPerspectiveTransform(src_points, dst_points)
    rotated = cv2.warpPerspective(img, M, (width, height), borderMode=cv2.BORDER_REPLICATE)
    
    return rotated


def create_combined_effects_video(
    image_path: str,
    output_path: str,
    duration: float = 5.0,
    fps: int = 30
) -> bool:
    """
    複数のエフェクトを組み合わせた動画を生成
    
    Args:
        image_path: 入力画像のパス
        output_path: 出力動画のパス
        duration: 動画の長さ（秒）
        fps: フレームレート
    
    Returns:
        成功した場合はTrue
    """
    if not os.path.exists(image_path):
        print(f"[ERROR] 入力画像が見つかりません: {image_path}")
        return False
    
    print(f"\n[複合エフェクト] 動画生成中...")
    print(f"   入力画像: {image_path}")
    print(f"   長さ: {duration}秒")
    
    # 画像を読み込み
    img = cv2.imread(image_path)
    if img is None:
        print(f"[ERROR] 画像の読み込みに失敗: {image_path}")
        return False
    
    height, width = img.shape[:2]
    total_frames = int(duration * fps)
    
    # VideoWriterの初期化
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not video_writer.isOpened():
        print("[ERROR] VideoWriterの初期化に失敗")
        return False
    
    center_x, center_y = width // 2, height // 2
    
    for i in range(total_frames):
        progress = i / total_frames
        
        # 複数のエフェクトを組み合わせ
        # 1. ゆっくりズームイン
        scale = 1.0 + (0.15 * progress)
        frame = zoom_image(img, scale)
        
        # 2. 微妙なY軸回転
        angle = math.sin(progress * math.pi * 2) * 8
        frame = rotate_3d_y(frame, angle, center_x, center_y)
        
        # 3. 微妙なパン
        offset_x = int(math.sin(progress * math.pi * 2) * width * 0.03)
        frame = pan_image(frame, offset_x, 0)
        
        video_writer.write(frame)
        
        if (i + 1) % 30 == 0:
            print(f"   進捗: {i+1}/{total_frames} フレーム")
    
    video_writer.release()
    
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n[OK] 動画を保存しました: {output_path}")
    print(f"   ファイルサイズ: {file_size_mb:.2f} MB")
    
    return True


def main():
    """メイン関数"""
    print("=" * 70)
    print("1枚の画像から動くアニメーション動画を生成")
    print("=" * 70)
    
    # 入力画像
    input_image = "verification/sample_tshirt.png"
    
    # 生成された画像がある場合はそちらを使用
    if os.path.exists("verification/virtual_tryon_result_1.png"):
        input_image = "verification/virtual_tryon_result_1.png"
        print(f"\n[INFO] 生成済み画像を使用します: {input_image}")
    elif not os.path.exists(input_image):
        print(f"\n[ERROR] 入力画像が見つかりません: {input_image}")
        return False
    
    print("\n選択してください：")
    print("1. Ken Burns効果（ズームイン）")
    print("2. Ken Burns効果（ズームアウト）")
    print("3. Ken Burns効果（ズーム+パン）")
    print("4. 3D回転効果（Y軸）")
    print("5. 3D回転効果（X軸）")
    print("6. 複合エフェクト（推奨）")
    print("7. すべてのエフェクトを生成")
    
    try:
        choice = input("\n選択 (1-7): ").strip()
    except:
        choice = "6"  # デフォルト
    
    success = True
    
    if choice == "1":
        success = create_ken_burns_video(
            input_image,
            "verification/animated_zoom_in.mp4",
            duration=3.0,
            effect="zoom_in"
        )
    elif choice == "2":
        success = create_ken_burns_video(
            input_image,
            "verification/animated_zoom_out.mp4",
            duration=3.0,
            effect="zoom_out"
        )
    elif choice == "3":
        success = create_ken_burns_video(
            input_image,
            "verification/animated_zoom_pan.mp4",
            duration=3.0,
            effect="zoom_pan"
        )
    elif choice == "4":
        success = create_3d_rotation_video(
            input_image,
            "verification/animated_3d_y.mp4",
            duration=3.0,
            rotation_axis="y"
        )
    elif choice == "5":
        success = create_3d_rotation_video(
            input_image,
            "verification/animated_3d_x.mp4",
            duration=3.0,
            rotation_axis="x"
        )
    elif choice == "6":
        success = create_combined_effects_video(
            input_image,
            "verification/animated_combined.mp4",
            duration=5.0
        )
    elif choice == "7":
        print("\n[INFO] すべてのエフェクトを生成します...")
        effects = [
            ("zoom_in", "animated_zoom_in.mp4"),
            ("zoom_pan", "animated_zoom_pan.mp4"),
            ("3d_y", "animated_3d_y.mp4"),
            ("combined", "animated_combined.mp4"),
        ]
        
        for effect_name, filename in effects:
            output_path = f"verification/{filename}"
            if effect_name == "zoom_in":
                create_ken_burns_video(input_image, output_path, 3.0, 30, "zoom_in")
            elif effect_name == "zoom_pan":
                create_ken_burns_video(input_image, output_path, 3.0, 30, "zoom_pan")
            elif effect_name == "3d_y":
                create_3d_rotation_video(input_image, output_path, 3.0, 30, "y")
            elif effect_name == "combined":
                create_combined_effects_video(input_image, output_path, 5.0, 30)
    else:
        print("\n[ERROR] 無効な選択です")
        success = False
    
    if success:
        print("\n" + "=" * 70)
        print("[SUCCESS] 動画生成完了！")
        print("=" * 70)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


