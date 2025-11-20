"""Reference person data model"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ReferencePerson:
    """参考人物を表すデータクラス
    
    この人物の画像を参考にして、指定された服を着せた画像を生成します
    """
    
    image_path: str
    name: str = "参考人物"
    description: Optional[str] = None  # 人物の特徴（自動抽出）
    
    def __post_init__(self):
        """バリデーション"""
        if not Path(self.image_path).exists():
            raise ValueError(f"Image file not found: {self.image_path}")
    
    @property
    def display_name(self) -> str:
        """表示用の名前"""
        return f"{self.name}: {Path(self.image_path).name}"
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "image_path": self.image_path,
            "name": self.name,
            "description": self.description,
        }

