"""Configuration management"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class ConfigManager:
    """設定管理クラス"""

    def __init__(self, env_file: Optional[Path] = None):
        """
        Args:
            env_file: .envファイルのパス（Noneの場合はデフォルト）
        """
        if env_file is None:
            env_file = Path(__file__).parent.parent.parent / ".env"

        self.env_file = env_file

        # .envファイルが存在する場合は読み込み
        if self.env_file.exists():
            load_dotenv(self.env_file)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        環境変数を取得

        Args:
            key: キー名
            default: デフォルト値

        Returns:
            値（存在しない場合はdefault）
        """
        return os.getenv(key, default)

    def get_int(self, key: str, default: int = 0) -> int:
        """整数値を取得"""
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """浮動小数点数を取得"""
        value = self.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """ブール値を取得"""
        value = self.get(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    @property
    def max_retries(self) -> int:
        """最大リトライ回数"""
        return self.get_int("MAX_RETRIES", 3)

    @property
    def request_timeout(self) -> int:
        """リクエストタイムアウト（秒）"""
        return self.get_int("REQUEST_TIMEOUT", 60)

    @property
    def log_level(self) -> str:
        """ログレベル"""
        return self.get("LOG_LEVEL", "INFO")




