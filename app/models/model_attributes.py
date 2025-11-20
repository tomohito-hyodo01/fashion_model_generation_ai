"""Model attributes data model"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelAttributes:
    """モデル（人物）属性を表すデータクラス"""

    gender: str = "female"  # male/female
    age_range: str = "20s"  # 10s/20s/30s/40s/50s+
    ethnicity: str = "asian"  # asian/european/african/american/oceanian/mixed
    body_type: str = "standard"  # slim/standard/athletic/plus-size
    height: str = "standard"  # short/standard/tall
    pose: str = "front"  # front/side/walking/sitting/custom
    background: str = "white"  # white/transparent/studio/location/custom
    custom_description: Optional[str] = None  # カスタム記述

    def __post_init__(self):
        """バリデーション"""
        valid_genders = ["male", "female"]
        if self.gender not in valid_genders:
            raise ValueError(f"Invalid gender: {self.gender}")

        valid_age_ranges = ["10s", "20s", "30s", "40s", "50s+"]
        if self.age_range not in valid_age_ranges:
            raise ValueError(f"Invalid age_range: {self.age_range}")
        
        valid_ethnicities = ["asian", "european", "african", "american", "oceanian", "mixed"]
        if self.ethnicity not in valid_ethnicities:
            raise ValueError(f"Invalid ethnicity: {self.ethnicity}")

    def to_description(self) -> str:
        """プロンプト用の描写を生成"""
        # 地域の表現を改善
        region_descriptions = {
            "asian": "from Asia",
            "european": "from Europe",
            "african": "from Africa",
            "american": "from the Americas",
            "oceanian": "from Oceania",
            "mixed": "of mixed heritage"
        }
        
        region_desc = region_descriptions.get(self.ethnicity, "")
        
        # 人物を最優先に記述
        desc = (
            f"A REAL HUMAN {self.gender} fashion model {region_desc}, "
            f"{self.age_range} years old, "
            f"{self.body_type} body type"
        )
        
        return desc

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "gender": self.gender,
            "age_range": self.age_range,
            "ethnicity": self.ethnicity,
            "body_type": self.body_type,
            "height": self.height,
            "pose": self.pose,
            "background": self.background,
            "custom_description": self.custom_description,
        }

