"""Clothing item data model"""

from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class ClothingItem:
    """衣類アイテムを表すデータクラス"""

    image_path: str
    clothing_type: str  # TOP/BOTTOM/OUTER/ONE_PIECE/ACCESSORY
    colors: List[str] = field(default_factory=list)  # Hex値のリスト
    pattern: str = "solid"  # solid/stripe/check/dot等
    material: str = "unknown"  # cotton/denim/silk等
    analyzed_description: str = ""  # 詳細な英語描写
    mask_path: Optional[str] = None  # セグメンテーションマスク
    fingerprint: Optional[dict] = None  # 色・柄フィンガープリント

    def __post_init__(self):
        """バリデーション"""
        if not Path(self.image_path).exists():
            raise ValueError(f"Image file not found: {self.image_path}")

        valid_types = ["TOP", "BOTTOM", "OUTER", "ONE_PIECE", "ACCESSORY"]
        if self.clothing_type not in valid_types:
            raise ValueError(
                f"Invalid clothing_type: {self.clothing_type}. "
                f"Must be one of {valid_types}"
            )

    @property
    def display_name(self) -> str:
        """表示用の名前"""
        return f"{self.clothing_type}: {Path(self.image_path).name}"

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "image_path": self.image_path,
            "clothing_type": self.clothing_type,
            "colors": self.colors,
            "pattern": self.pattern,
            "material": self.material,
            "analyzed_description": self.analyzed_description,
            "mask_path": self.mask_path,
            "fingerprint": self.fingerprint,
        }




