"""Settings export and import manager"""

import json
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime


class SettingsManager:
    """設定のエクスポート・インポート管理"""
    
    def __init__(self):
        """初期化"""
        pass
    
    def export_settings(
        self,
        model_attrs: Dict,
        generation_config: Dict,
        garments_info: list,
        export_path: str
    ) -> bool:
        """
        現在の設定をJSONファイルにエクスポート
        
        Args:
            model_attrs: モデル属性
            generation_config: 生成設定
            garments_info: 衣類情報
            export_path: エクスポート先のパス
        
        Returns:
            成功した場合はTrue
        """
        try:
            # エクスポートデータを構築
            export_data = {
                "version": "2.0",
                "exported_at": datetime.now().isoformat(),
                "model_attributes": model_attrs,
                "generation_config": generation_config,
                "garments": garments_info
            }
            
            # JSONファイルに保存
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"[Settings] エクスポート完了: {export_path}")
            return True
        
        except Exception as e:
            print(f"[Settings] エクスポートエラー: {e}")
            return False
    
    def import_settings(self, import_path: str) -> Optional[Dict]:
        """
        JSONファイルから設定をインポート
        
        Args:
            import_path: インポート元のパス
        
        Returns:
            設定データ、またはNone
        """
        try:
            if not Path(import_path).exists():
                print(f"[Settings] ファイルが見つかりません: {import_path}")
                return None
            
            # JSONファイルを読み込み
            with open(import_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)
            
            # バージョンチェック
            version = import_data.get("version", "1.0")
            print(f"[Settings] インポート: バージョン {version}")
            
            # 設定を検証
            if not self._validate_settings(import_data):
                print("[Settings] 設定の検証に失敗しました")
                return None
            
            print(f"[Settings] インポート完了: {import_path}")
            
            return import_data
        
        except Exception as e:
            print(f"[Settings] インポートエラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _validate_settings(self, data: Dict) -> bool:
        """
        設定データを検証
        
        Args:
            data: 設定データ
        
        Returns:
            有効な場合はTrue
        """
        # 必須フィールドをチェック
        required_fields = ["model_attributes", "generation_config"]
        
        for field in required_fields:
            if field not in data:
                print(f"[Settings] 必須フィールドがありません: {field}")
                return False
        
        return True
    
    def create_preset(
        self,
        name: str,
        model_attrs: Dict,
        generation_config: Dict,
        description: str = ""
    ) -> Dict:
        """
        プリセットを作成
        
        Args:
            name: プリセット名
            model_attrs: モデル属性
            generation_config: 生成設定
            description: 説明
        
        Returns:
            プリセットデータ
        """
        preset = {
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "model_attributes": model_attrs,
            "generation_config": generation_config
        }
        
        return preset
    
    def save_preset(self, preset: Dict, preset_dir: str = None) -> bool:
        """
        プリセットを保存
        
        Args:
            preset: プリセットデータ
            preset_dir: プリセットディレクトリ
        
        Returns:
            成功した場合はTrue
        """
        if preset_dir is None:
            # デフォルトパス
            preset_dir = Path.home() / "AppData" / "Local" / "VirtualFashionTryOn" / "presets"
        else:
            preset_dir = Path(preset_dir)
        
        preset_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイル名を生成
        preset_name = preset["name"].replace(" ", "_").replace("/", "_")
        preset_file = preset_dir / f"{preset_name}.json"
        
        try:
            with open(preset_file, "w", encoding="utf-8") as f:
                json.dump(preset, f, ensure_ascii=False, indent=2)
            
            print(f"[Settings] プリセット保存: {preset_file}")
            return True
        
        except Exception as e:
            print(f"[Settings] プリセット保存エラー: {e}")
            return False
    
    def load_presets(self, preset_dir: str = None) -> List[Dict]:
        """
        プリセット一覧を読み込み
        
        Args:
            preset_dir: プリセットディレクトリ
        
        Returns:
            プリセットのリスト
        """
        if preset_dir is None:
            preset_dir = Path.home() / "AppData" / "Local" / "VirtualFashionTryOn" / "presets"
        else:
            preset_dir = Path(preset_dir)
        
        if not preset_dir.exists():
            return []
        
        presets = []
        
        for preset_file in preset_dir.glob("*.json"):
            try:
                with open(preset_file, "r", encoding="utf-8") as f:
                    preset = json.load(f)
                    presets.append(preset)
            except Exception as e:
                print(f"[Settings] プリセット読み込みエラー({preset_file.name}): {e}")
        
        print(f"[Settings] {len(presets)}個のプリセットを読み込みました")
        
        return presets


# テスト用
if __name__ == "__main__":
    print("=" * 70)
    print("Settings Manager テスト")
    print("=" * 70)
    
    manager = SettingsManager()
    
    # テストデータ
    test_model_attrs = {
        "gender": "female",
        "age_range": "20s",
        "ethnicity": "asian",
        "body_type": "standard",
        "pose": "front",
        "background": "white"
    }
    
    test_config = {
        "size": "1024x1024",
        "num_outputs": 2,
        "quality": "standard"
    }
    
    test_garments = [
        {"type": "TOP", "path": "test_top.png"},
        {"type": "BOTTOM", "path": "test_bottom.png"}
    ]
    
    # エクスポートテスト
    print("\n[TEST] エクスポート...")
    success = manager.export_settings(
        test_model_attrs,
        test_config,
        test_garments,
        "test_settings.json"
    )
    print(f"[OK] エクスポート: {success}")
    
    # インポートテスト
    if success:
        print("\n[TEST] インポート...")
        imported = manager.import_settings("test_settings.json")
        if imported:
            print(f"[OK] インポート成功")
            print(f"  - モデル属性: {imported['model_attributes']}")
            print(f"  - 生成設定: {imported['generation_config']}")
        else:
            print("[FAILED] インポート失敗")
    
    # プリセット作成テスト
    print("\n[TEST] プリセット作成...")
    preset = manager.create_preset(
        name="カジュアル女性 20代",
        model_attrs=test_model_attrs,
        generation_config=test_config,
        description="カジュアルな20代女性モデル"
    )
    print(f"[OK] プリセット作成: {preset['name']}")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] すべてのテスト完了")
    print("=" * 70)

