"""Generation configuration data model"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerationConfig:
    """生成設定を表すデータクラス"""

    provider: str  # openai/stability/vertex
    quality: str = "standard"  # standard/hd
    size: str = "1024x1024"  # 512x512/1024x1024/1024x1792/1792x1024
    num_outputs: int = 1  # 1-4
    seed: Optional[int] = None

    # Stability AI用パラメータ（SD 3.5対応）
    cfg_scale: float = 7.0  # 1-10（SD 3.5の上限は10）
    steps: int = 40  # 推奨範囲
    strength: float = 0.98  # 0.0-1.0（衣類→人物への変換度、極めて高く）

    # 詳細設定
    background_style: Optional[str] = None
    lighting: Optional[str] = None
    photography_style: Optional[str] = None

    def __post_init__(self):
        """バリデーション"""
        valid_providers = ["openai", "stability", "vertex", "gemini"]
        if self.provider not in valid_providers:
            raise ValueError(
                f"Invalid provider: {self.provider}. Must be one of {valid_providers}"
            )

        if not 1 <= self.num_outputs <= 4:
            raise ValueError(f"num_outputs must be 1-4, got {self.num_outputs}")

        valid_qualities = ["standard", "hd"]
        if self.quality not in valid_qualities:
            raise ValueError(f"Invalid quality: {self.quality}")

        # Stability AI用パラメータの範囲チェック（SD 3.5）
        if not 1 <= self.cfg_scale <= 10:
            raise ValueError(f"cfg_scale should be 1-10 (SD 3.5 limit), got {self.cfg_scale}")

        if not 1 <= self.steps <= 50:
            raise ValueError(f"steps should be 1-50, got {self.steps}")

        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(f"strength should be 0.0-1.0, got {self.strength}")

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "provider": self.provider,
            "quality": self.quality,
            "size": self.size,
            "num_outputs": self.num_outputs,
            "seed": self.seed,
            "cfg_scale": self.cfg_scale,
            "steps": self.steps,
            "strength": self.strength,
            "background_style": self.background_style,
            "lighting": self.lighting,
            "photography_style": self.photography_style,
        }

