"""Pose extraction using MediaPipe"""

import numpy as np
from PIL import Image
from typing import Dict, Optional, Tuple
from pathlib import Path


class PoseExtractor:
    """MediaPipeを使用してポーズを抽出"""
    
    def __init__(self):
        """初期化"""
        self.mediapipe_available = False
        self.pose_detector = None
        
        # MediaPipeのインポートを試みる
        try:
            import mediapipe as mp
            self.mp_pose = mp.solutions.pose
            self.mp_drawing = mp.solutions.drawing_utils
            self.mediapipe_available = True
            print("[INFO] MediaPipeが利用可能です")
        except ImportError:
            print("[WARN] MediaPipeがインストールされていません")
            print("       pip install mediapipe でインストールしてください")
    
    def extract_pose(self, image_path: str) -> Optional[Dict]:
        """画像からポーズを抽出
        
        Args:
            image_path: 入力画像のパス
        
        Returns:
            ポーズ情報の辞書、またはNone
            {
                'landmarks': ランドマーク座標のリスト,
                'description': テキスト記述,
                'pose_type': 推定されたポーズタイプ
            }
        """
        if not self.mediapipe_available:
            print("[WARN] MediaPipeが利用できないため、ポーズ抽出をスキップします")
            return None
        
        if not Path(image_path).exists():
            print(f"[ERROR] 画像が見つかりません: {image_path}")
            return None
        
        try:
            # 画像を読み込み
            image = Image.open(image_path)
            image_rgb = np.array(image.convert('RGB'))
            
            # ポーズ検出器を初期化（都度初期化）
            with self.mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,  # 0, 1, or 2
                enable_segmentation=False,
                min_detection_confidence=0.5
            ) as pose:
                # ポーズを検出
                results = pose.process(image_rgb)
                
                if not results.pose_landmarks:
                    print("[WARN] ポーズが検出できませんでした")
                    return None
                
                # ランドマークを抽出
                landmarks = self._extract_landmarks(results.pose_landmarks)
                
                # ポーズタイプを推定
                pose_type = self._estimate_pose_type(landmarks)
                
                # テキスト記述を生成
                description = self._generate_description(landmarks, pose_type)
                
                return {
                    'landmarks': landmarks,
                    'description': description,
                    'pose_type': pose_type,
                    'confidence': 0.8  # TODO: 実際の信頼度を計算
                }
        
        except Exception as e:
            print(f"[ERROR] ポーズ抽出エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_landmarks(self, pose_landmarks) -> Dict[str, Tuple[float, float, float]]:
        """ランドマーク座標を抽出"""
        landmarks = {}
        
        # 主要なランドマークを抽出
        landmark_names = {
            0: 'nose',
            11: 'left_shoulder',
            12: 'right_shoulder',
            13: 'left_elbow',
            14: 'right_elbow',
            15: 'left_wrist',
            16: 'right_wrist',
            23: 'left_hip',
            24: 'right_hip',
            25: 'left_knee',
            26: 'right_knee',
            27: 'left_ankle',
            28: 'right_ankle',
        }
        
        for idx, name in landmark_names.items():
            lm = pose_landmarks.landmark[idx]
            landmarks[name] = (lm.x, lm.y, lm.z)
        
        return landmarks
    
    def _estimate_pose_type(self, landmarks: Dict) -> str:
        """ランドマークからポーズタイプを推定"""
        # 肩と腰のY座標を取得
        left_shoulder_y = landmarks['left_shoulder'][1]
        right_shoulder_y = landmarks['right_shoulder'][1]
        left_hip_y = landmarks['left_hip'][1]
        right_hip_y = landmarks['right_hip'][1]
        
        # 膝と足首のY座標
        left_knee_y = landmarks['left_knee'][1]
        right_knee_y = landmarks['right_knee'][1]
        left_ankle_y = landmarks['left_ankle'][1]
        right_ankle_y = landmarks['right_ankle'][1]
        
        # 肩のY座標の平均
        shoulder_y = (left_shoulder_y + right_shoulder_y) / 2
        hip_y = (left_hip_y + right_hip_y) / 2
        
        # 膝が曲がっているか（座位の判定）
        left_knee_bent = (left_knee_y - left_hip_y) < 0.3 * (left_ankle_y - left_hip_y)
        right_knee_bent = (right_knee_y - right_hip_y) < 0.3 * (right_ankle_y - right_hip_y)
        
        if left_knee_bent and right_knee_bent:
            return "sitting"
        
        # 左右の足の位置差（歩行の判定）
        foot_diff = abs(left_ankle_y - right_ankle_y)
        if foot_diff > 0.1:
            return "walking"
        
        # 腕の位置
        left_elbow_x = landmarks['left_elbow'][0]
        right_elbow_x = landmarks['right_elbow'][0]
        left_shoulder_x = landmarks['left_shoulder'][0]
        right_shoulder_x = landmarks['right_shoulder'][0]
        
        # 腕組み（腕がクロスしている）
        if abs(left_elbow_x - right_shoulder_x) < 0.2 and abs(right_elbow_x - left_shoulder_x) < 0.2:
            return "arms_crossed"
        
        # デフォルトは立位
        return "front"
    
    def _generate_description(self, landmarks: Dict, pose_type: str) -> str:
        """ポーズの詳細な記述を生成"""
        descriptions = {
            "front": "standing straight, facing camera, full body visible from head to feet",
            "sitting": "sitting position with knees bent, full body visible",
            "walking": "walking pose with one leg forward, dynamic stance",
            "arms_crossed": "standing with arms crossed, confident pose",
        }
        
        base_description = descriptions.get(pose_type, "standing in natural pose")
        
        # 手の位置を追加
        left_wrist_y = landmarks['left_wrist'][1]
        right_wrist_y = landmarks['right_wrist'][1]
        left_hip_y = landmarks['left_hip'][1]
        
        if left_wrist_y < left_hip_y - 0.2 and right_wrist_y < left_hip_y - 0.2:
            base_description += ", hands raised"
        elif abs(left_wrist_y - left_hip_y) < 0.1 and abs(right_wrist_y - left_hip_y) < 0.1:
            base_description += ", hands on hips"
        
        return base_description
    
    def visualize_pose(self, image_path: str, output_path: Optional[str] = None) -> Optional[Image.Image]:
        """ポーズをビジュアライズ（デバッグ用）
        
        Args:
            image_path: 入力画像のパス
            output_path: 出力画像のパス（Noneの場合は保存しない）
        
        Returns:
            ビジュアライズされた画像、またはNone
        """
        if not self.mediapipe_available:
            return None
        
        try:
            import cv2
            
            # 画像を読み込み
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # ポーズを検出
            with self.mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,
                enable_segmentation=False,
                min_detection_confidence=0.5
            ) as pose:
                results = pose.process(image_rgb)
                
                if results.pose_landmarks:
                    # ランドマークを描画
                    self.mp_drawing.draw_landmarks(
                        image,
                        results.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS,
                        self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                    )
            
            # PIL Imageに変換
            result_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # 保存
            if output_path:
                result_image.save(output_path)
                print(f"[INFO] ポーズビジュアライズを保存: {output_path}")
            
            return result_image
        
        except Exception as e:
            print(f"[ERROR] ビジュアライズエラー: {e}")
            return None


# 使用例
if __name__ == "__main__":
    extractor = PoseExtractor()
    
    # テスト画像
    test_image = "verification/sample_tshirt.png"
    
    if Path(test_image).exists():
        print(f"\n[TEST] ポーズ抽出テスト: {test_image}")
        pose_info = extractor.extract_pose(test_image)
        
        if pose_info:
            print(f"[OK] ポーズタイプ: {pose_info['pose_type']}")
            print(f"[OK] 記述: {pose_info['description']}")
            print(f"[OK] ランドマーク数: {len(pose_info['landmarks'])}")
        else:
            print("[FAILED] ポーズ抽出に失敗")
    else:
        print(f"[ERROR] テスト画像が見つかりません: {test_image}")


