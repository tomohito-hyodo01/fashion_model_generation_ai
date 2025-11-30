"""API key management with encryption"""

import os
import json
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet

# Windows DPAPI（利用可能な場合）
try:
    import win32crypt

    DPAPI_AVAILABLE = True
except ImportError:
    DPAPI_AVAILABLE = False


class APIKeyManager:
    """APIキーを暗号化して保存・管理"""

    def __init__(self, config_dir: Optional[Path] = None, use_dpapi: bool = True):
        """
        Args:
            config_dir: 設定ディレクトリ（Noneの場合はユーザーホーム）
            use_dpapi: Windows DPAPIを使用するか（Windowsの場合）
        """
        if config_dir is None:
            config_dir = Path.home() / ".virtual_fashion_tryon"

        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.use_dpapi = use_dpapi and DPAPI_AVAILABLE and os.name == "nt"

        if not self.use_dpapi:
            # Fernetを使用（DPAPIが利用できない場合）
            self.key_file = self.config_dir / ".key"
            self.key = self._load_or_create_key()
            self.cipher = Fernet(self.key)

        self.credentials_file = self.config_dir / ".credentials"

    def _load_or_create_key(self) -> bytes:
        """暗号化キーを読み込みまたは生成（Fernet用）"""
        if self.key_file.exists():
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            # キーファイルのパーミッションを制限（Unix系）
            if os.name != "nt":
                os.chmod(self.key_file, 0o600)
            return key

    def save_api_key(self, service: str, api_key: str) -> None:
        """
        APIキーを暗号化して保存

        Args:
            service: サービス名（openai/stability/google）
            api_key: APIキー
        """
        credentials = self._load_credentials()

        if self.use_dpapi:
            # Windows DPAPIで暗号化
            encrypted = win32crypt.CryptProtectData(
                api_key.encode(), None, None, None, None, 0
            )
            credentials[service] = encrypted.hex()
        else:
            # Fernetで暗号化
            encrypted = self.cipher.encrypt(api_key.encode())
            credentials[service] = encrypted.decode()

        self._save_credentials(credentials)

    def load_api_key(self, service: str) -> Optional[str]:
        """
        APIキーを復号化して読み込み

        Args:
            service: サービス名

        Returns:
            APIキー（存在しない場合はNone）
        """
        credentials = self._load_credentials()

        if service not in credentials:
            return None

        if self.use_dpapi:
            # Windows DPAPIで復号化
            encrypted = bytes.fromhex(credentials[service])
            _, decrypted = win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)
            return decrypted.decode()
        else:
            # Fernetで復号化
            encrypted = credentials[service].encode()
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode()

    def delete_api_key(self, service: str) -> None:
        """
        APIキーを削除

        Args:
            service: サービス名
        """
        credentials = self._load_credentials()

        if service in credentials:
            del credentials[service]
            self._save_credentials(credentials)

    def list_services(self) -> list:
        """保存されているサービスのリストを取得"""
        credentials = self._load_credentials()
        return list(credentials.keys())

    def _load_credentials(self) -> dict:
        """認証情報ファイルを読み込み"""
        if not self.credentials_file.exists():
            return {}

        with open(self.credentials_file, "r") as f:
            return json.load(f)

    def _save_credentials(self, credentials: dict) -> None:
        """認証情報ファイルを保存"""
        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f)

        # ファイルのパーミッションを制限（Unix系）
        if os.name != "nt":
            os.chmod(self.credentials_file, 0o600)




