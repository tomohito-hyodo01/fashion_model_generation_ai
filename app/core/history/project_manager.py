"""Project management for multiple generation sessions"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class ProjectManager:
    """プロジェクト管理
    
    複数の生成セッションをプロジェクトとして管理します
    """
    
    def __init__(self, projects_dir: str = None):
        """
        Args:
            projects_dir: プロジェクトディレクトリ（Noneの場合はデフォルト）
        """
        if projects_dir is None:
            # デフォルトパス: ユーザーのDocumentsフォルダ
            docs = Path.home() / "Documents" / "VirtualFashionTryOn" / "Projects"
            docs.mkdir(parents=True, exist_ok=True)
            projects_dir = str(docs)
        
        self.projects_dir = Path(projects_dir)
        self.current_project = None
    
    def create_project(
        self,
        name: str,
        description: str = "",
        tags: Optional[List[str]] = None
    ) -> Dict:
        """
        新しいプロジェクトを作成
        
        Args:
            name: プロジェクト名
            description: プロジェクトの説明
            tags: タグのリスト
        
        Returns:
            プロジェクト情報
        """
        # プロジェクトIDを生成（タイムスタンプベース）
        project_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # プロジェクトディレクトリを作成
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # サブディレクトリを作成
        (project_dir / "images").mkdir(exist_ok=True)
        (project_dir / "garments").mkdir(exist_ok=True)
        
        # プロジェクトメタデータ
        project_data = {
            "id": project_id,
            "name": name,
            "description": description,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "generation_count": 0,
            "image_count": 0
        }
        
        # メタデータを保存
        with open(project_dir / "project.json", "w", encoding="utf-8") as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
        
        self.current_project = project_data
        
        print(f"[Project] プロジェクト作成: {name} (ID: {project_id})")
        
        return project_data
    
    def open_project(self, project_id: str) -> Optional[Dict]:
        """
        プロジェクトを開く
        
        Args:
            project_id: プロジェクトID
        
        Returns:
            プロジェクト情報、またはNone
        """
        project_dir = self.projects_dir / project_id
        metadata_file = project_dir / "project.json"
        
        if not metadata_file.exists():
            print(f"[Project] プロジェクトが見つかりません: {project_id}")
            return None
        
        with open(metadata_file, "r", encoding="utf-8") as f:
            project_data = json.load(f)
        
        self.current_project = project_data
        
        print(f"[Project] プロジェクト読み込み: {project_data['name']}")
        
        return project_data
    
    def save_to_project(
        self,
        images: List,
        parameters: Dict,
        generation_name: str = ""
    ) -> str:
        """
        現在のプロジェクトに生成結果を保存
        
        Args:
            images: 生成画像のリスト
            parameters: 生成パラメータ
            generation_name: 生成名
        
        Returns:
            生成ID
        """
        if not self.current_project:
            raise RuntimeError("プロジェクトが開かれていません")
        
        project_dir = self.projects_dir / self.current_project["id"]
        
        # 生成IDを作成
        generation_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        generation_dir = project_dir / "images" / generation_id
        generation_dir.mkdir(parents=True, exist_ok=True)
        
        # 画像を保存
        for i, img in enumerate(images):
            img_path = generation_dir / f"image_{i+1}.png"
            img.save(img_path)
        
        # パラメータを保存
        generation_metadata = {
            "id": generation_id,
            "name": generation_name or f"Generation {self.current_project['generation_count'] + 1}",
            "created_at": datetime.now().isoformat(),
            "parameters": parameters,
            "image_count": len(images)
        }
        
        with open(generation_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(generation_metadata, f, ensure_ascii=False, indent=2)
        
        # プロジェクトメタデータを更新
        self.current_project["generation_count"] += 1
        self.current_project["image_count"] += len(images)
        self.current_project["updated_at"] = datetime.now().isoformat()
        
        with open(project_dir / "project.json", "w", encoding="utf-8") as f:
            json.dump(self.current_project, f, ensure_ascii=False, indent=2)
        
        print(f"[Project] 生成結果を保存: {generation_id}")
        
        return generation_id
    
    def list_projects(self) -> List[Dict]:
        """
        プロジェクト一覧を取得
        
        Returns:
            プロジェクト情報のリスト
        """
        projects = []
        
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                metadata_file = project_dir / "project.json"
                if metadata_file.exists():
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        project_data = json.load(f)
                        projects.append(project_data)
        
        # 更新日時でソート
        projects.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return projects
    
    def export_project(self, project_id: str, export_path: str) -> bool:
        """
        プロジェクトをエクスポート
        
        Args:
            project_id: プロジェクトID
            export_path: エクスポート先のパス（zipファイル）
        
        Returns:
            成功した場合はTrue
        """
        project_dir = self.projects_dir / project_id
        
        if not project_dir.exists():
            print(f"[Project] プロジェクトが見つかりません: {project_id}")
            return False
        
        try:
            # zipファイルを作成
            export_path_obj = Path(export_path)
            if export_path_obj.suffix != ".zip":
                export_path = str(export_path_obj) + ".zip"
            
            shutil.make_archive(
                export_path.replace(".zip", ""),
                'zip',
                project_dir
            )
            
            print(f"[Project] エクスポート完了: {export_path}")
            return True
        
        except Exception as e:
            print(f"[Project] エクスポートエラー: {e}")
            return False
    
    def import_project(self, import_path: str) -> Optional[Dict]:
        """
        プロジェクトをインポート
        
        Args:
            import_path: インポート元のパス（zipファイル）
        
        Returns:
            プロジェクト情報、またはNone
        """
        try:
            import_path_obj = Path(import_path)
            
            if not import_path_obj.exists():
                print(f"[Project] ファイルが見つかりません: {import_path}")
                return None
            
            # 一時ディレクトリに展開
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                shutil.unpack_archive(import_path, temp_dir, 'zip')
                
                # project.jsonを探す
                metadata_file = Path(temp_dir) / "project.json"
                if not metadata_file.exists():
                    print("[Project] project.jsonが見つかりません")
                    return None
                
                with open(metadata_file, "r", encoding="utf-8") as f:
                    project_data = json.load(f)
                
                # 新しいプロジェクトIDを生成
                new_project_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                project_data["id"] = new_project_id
                
                # プロジェクトディレクトリにコピー
                new_project_dir = self.projects_dir / new_project_id
                shutil.copytree(temp_dir, new_project_dir)
                
                # メタデータを更新
                with open(new_project_dir / "project.json", "w", encoding="utf-8") as f:
                    json.dump(project_data, f, ensure_ascii=False, indent=2)
            
            print(f"[Project] インポート完了: {project_data['name']} (ID: {new_project_id})")
            
            return project_data
        
        except Exception as e:
            print(f"[Project] インポートエラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def delete_project(self, project_id: str) -> bool:
        """
        プロジェクトを削除
        
        Args:
            project_id: プロジェクトID
        
        Returns:
            成功した場合はTrue
        """
        project_dir = self.projects_dir / project_id
        
        if not project_dir.exists():
            print(f"[Project] プロジェクトが見つかりません: {project_id}")
            return False
        
        try:
            shutil.rmtree(project_dir)
            
            if self.current_project and self.current_project["id"] == project_id:
                self.current_project = None
            
            print(f"[Project] プロジェクト削除: {project_id}")
            return True
        
        except Exception as e:
            print(f"[Project] 削除エラー: {e}")
            return False


# テスト用
if __name__ == "__main__":
    from PIL import Image
    
    print("=" * 70)
    print("Project Manager テスト")
    print("=" * 70)
    
    # テスト用ディレクトリ
    manager = ProjectManager("test_projects")
    
    # プロジェクトを作成
    print("\n[TEST] プロジェクトを作成...")
    project = manager.create_project(
        name="春夏コレクション",
        description="2025年春夏シーズンの衣類",
        tags=["spring", "summer", "2025"]
    )
    print(f"[OK] プロジェクト作成: {project['name']} (ID: {project['id']})")
    
    # ダミー画像を保存
    print("\n[TEST] 生成結果を保存...")
    dummy_img = Image.new('RGB', (100, 100), color='blue')
    generation_id = manager.save_to_project(
        images=[dummy_img],
        parameters={"test": "data"},
        generation_name="テスト生成1"
    )
    print(f"[OK] 生成結果保存: {generation_id}")
    
    # プロジェクト一覧を取得
    print("\n[TEST] プロジェクト一覧を取得...")
    projects = manager.list_projects()
    print(f"[OK] プロジェクト数: {len(projects)}")
    for p in projects:
        print(f"  - {p['name']}: 生成{p['generation_count']}回, 画像{p['image_count']}枚")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] すべてのテスト完了")
    print("=" * 70)


