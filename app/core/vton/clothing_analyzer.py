"""Clothing image analysis"""

from typing import Dict, List
import numpy as np
import cv2
from PIL import Image

try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class ClothingAnalyzer:
    """衣類画像を分析して詳細な描写を生成"""

    def analyze_clothing(self, image_path: str) -> Dict:
        """
        画像から衣類の特徴を抽出

        Args:
            image_path: 衣類画像のパス

        Returns:
            特徴辞書 {colors, pattern, texture, etc.}
        """
        # 日本語パスに対応した画像読み込み
        try:
            # PILで読み込んでからnumpy配列に変換
            from pathlib import Path
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            pil_img = Image.open(image_path)
            img_rgb = np.array(pil_img.convert('RGB'))
            
            if img_rgb.size == 0:
                raise ValueError(f"Failed to read image data from: {image_path}")
            
            # OpenCV形式（BGR）に変換
            img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Error loading image: {e}")
            raise ValueError(f"Failed to load image. Error: {str(e)}")

        return {
            "colors": self._extract_dominant_colors(img_rgb),
            "pattern": self._detect_pattern(img_rgb),
            "texture": self._analyze_texture(img_rgb),
            "edges": self._detect_edges(img),
        }

    def generate_detailed_description(
        self, features: Dict, clothing_type: str
    ) -> str:
        """
        特徴から非常に詳細な英語描写を生成

        Args:
            features: analyze_clothingで得た特徴
            clothing_type: 衣類タイプ

        Returns:
            非常に詳細な英語描写
        """
        parts = []

        # 衣類タイプを詳細に
        type_descriptions = {
            "TOP": "short-sleeved crew neck t-shirt",
            "BOTTOM": "straight-leg casual pants",
            "OUTER": "tailored blazer jacket",
            "ONE_PIECE": "knee-length dress",
            "ACCESSORY": "fashion accessory"
        }
        type_name = type_descriptions.get(clothing_type, clothing_type.lower())
        
        # 色の詳細記述（最重要）
        if features.get("colors"):
            colors = features["colors"]
            if len(colors) >= 1:
                # 主要色を非常に具体的に記述
                main_color = colors[0]
                parts.append(f"{type_name} in exact color {main_color}")
                
                if len(colors) > 1:
                    parts.append(f"with secondary color {colors[1]}")
        else:
            parts.append(f"{type_name}")

        # パターンの記述
        pattern = features.get("pattern", "solid")
        if pattern == "solid":
            parts.append("solid color")
        elif pattern == "simple":
            parts.append("with simple design details")
        elif pattern == "complex":
            parts.append("with detailed pattern design")

        # テクスチャの記述
        texture = features.get("texture", "medium")
        if texture == "smooth":
            parts.append("smooth fabric like cotton or polyester")
        elif texture == "rough":
            parts.append("textured fabric like knit or tweed")

        # 重要：正確な色の強調
        if features.get("colors"):
            parts.append(f"IMPORTANT: use exact color {features['colors'][0]} for this garment")

        return ", ".join(parts)

    def _describe_colors_detailed(self, hex_colors: List[str]) -> str:
        """色を詳細に記述"""
        if not hex_colors:
            return "neutral tones"
        
        if len(hex_colors) == 1:
            return f"solid {hex_colors[0]} color"
        elif len(hex_colors) == 2:
            return f"{hex_colors[0]} and {hex_colors[1]} colors"
        else:
            return f"multiple colors including {hex_colors[0]}, {hex_colors[1]}"

    def _extract_dominant_colors(
        self, img: np.ndarray, n_colors: int = 3
    ) -> List[str]:
        """主要色を抽出（Hex値）"""
        if SKLEARN_AVAILABLE:
            # K-meansクラスタリングを使用
            pixels = img.reshape(-1, 3)
            kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            colors = kmeans.cluster_centers_.astype(int)
        else:
            # フォールバック: 画像の平均色を使用
            mean_color = np.mean(img.reshape(-1, 3), axis=0).astype(int)
            colors = [mean_color]

        # Hex値に変換
        hex_colors = [self._rgb_to_hex(color) for color in colors]

        return hex_colors

    def _rgb_to_hex(self, rgb: np.ndarray) -> str:
        """RGB値をHex値に変換"""
        return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

    def _detect_pattern(self, img: np.ndarray) -> str:
        """パターン検出（簡易版）"""
        # グレースケールに変換
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # エッジ検出
        edges = cv2.Canny(gray, 50, 150)

        # エッジの密度でパターンを判定
        edge_density = np.sum(edges > 0) / edges.size

        if edge_density < 0.05:
            return "solid"
        elif edge_density < 0.15:
            return "simple"
        else:
            return "complex"

    def _analyze_texture(self, img: np.ndarray) -> str:
        """テクスチャ分析（簡易版）"""
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # 標準偏差でテクスチャの複雑さを判定
        std_dev = np.std(gray)

        if std_dev < 30:
            return "smooth"
        elif std_dev < 60:
            return "medium"
        else:
            return "rough"

    def _detect_edges(self, img: np.ndarray) -> np.ndarray:
        """Cannyエッジ検出"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        return edges

    def _describe_colors(self, hex_colors: List[str]) -> str:
        """色リストから説明文を生成"""
        if not hex_colors:
            return "unknown color"

        # 最も支配的な色を返す
        return hex_colors[0]

