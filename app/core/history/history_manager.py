"""Generation history management"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from PIL import Image
import base64
from io import BytesIO


class HistoryManager:
    """生成履歴管理
    
    生成された画像とそのパラメータをデータベースに保存・管理します
    """
    
    def __init__(self, db_path: str = None):
        """
        Args:
            db_path: データベースファイルのパス（Noneの場合はデフォルト）
        """
        if db_path is None:
            # デフォルトパス: ユーザーのAppDataフォルダ
            app_data = Path.home() / "AppData" / "Local" / "VirtualFashionTryOn"
            app_data.mkdir(parents=True, exist_ok=True)
            db_path = str(app_data / "history.db")
        
        self.db_path = db_path
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        """データベースを初期化"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # 履歴テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                generation_mode TEXT NOT NULL,
                num_images INTEGER NOT NULL,
                parameters TEXT NOT NULL,
                is_favorite INTEGER DEFAULT 0,
                tags TEXT,
                notes TEXT
            )
        """)
        
        # 画像テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                history_id INTEGER NOT NULL,
                image_index INTEGER NOT NULL,
                image_data BLOB NOT NULL,
                thumbnail_data BLOB,
                angle INTEGER,
                FOREIGN KEY (history_id) REFERENCES generation_history(id)
            )
        """)
        
        # インデックス
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON generation_history(created_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_favorite 
            ON generation_history(is_favorite DESC, created_at DESC)
        """)
        
        self.conn.commit()
    
    def save_generation(
        self,
        images: List[Image.Image],
        parameters: Dict,
        generation_mode: str = "variety",
        angles: Optional[List[int]] = None,
        tags: Optional[List[str]] = None,
        notes: str = ""
    ) -> int:
        """
        生成結果を保存
        
        Args:
            images: 生成画像のリスト
            parameters: 生成パラメータ
            generation_mode: 生成モード（variety/angle）
            angles: 各画像の角度（マルチアングルの場合）
            tags: タグのリスト
            notes: メモ
        
        Returns:
            履歴ID
        """
        cursor = self.conn.cursor()
        
        # パラメータをJSON化
        params_json = json.dumps(parameters, ensure_ascii=False)
        tags_json = json.dumps(tags or [], ensure_ascii=False)
        
        # 履歴レコードを作成
        cursor.execute("""
            INSERT INTO generation_history 
            (created_at, generation_mode, num_images, parameters, tags, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            generation_mode,
            len(images),
            params_json,
            tags_json,
            notes
        ))
        
        history_id = cursor.lastrowid
        
        # 各画像を保存
        for i, img in enumerate(images):
            # フルサイズ画像
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            
            # サムネイル
            thumb = img.copy()
            thumb.thumbnail((200, 200), Image.Resampling.LANCZOS)
            thumb_buffer = BytesIO()
            thumb.save(thumb_buffer, format='PNG')
            thumb_data = thumb_buffer.getvalue()
            
            # 角度情報
            angle = angles[i] if angles and i < len(angles) else None
            
            cursor.execute("""
                INSERT INTO history_images 
                (history_id, image_index, image_data, thumbnail_data, angle)
                VALUES (?, ?, ?, ?, ?)
            """, (history_id, i, img_data, thumb_data, angle))
        
        self.conn.commit()
        
        print(f"[History] 履歴保存完了: ID={history_id}, 画像数={len(images)}")
        
        return history_id
    
    def get_history_list(
        self,
        limit: int = 50,
        favorites_only: bool = False,
        tag_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        履歴リストを取得
        
        Args:
            limit: 取得件数
            favorites_only: お気に入りのみ
            tag_filter: タグでフィルタ
        
        Returns:
            履歴のリスト
        """
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM generation_history WHERE 1=1"
        params = []
        
        if favorites_only:
            query += " AND is_favorite = 1"
        
        if tag_filter:
            query += " AND tags LIKE ?"
            params.append(f'%"{tag_filter}"%')
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        history_list = []
        for row in rows:
            history_list.append({
                "id": row["id"],
                "created_at": row["created_at"],
                "generation_mode": row["generation_mode"],
                "num_images": row["num_images"],
                "parameters": json.loads(row["parameters"]),
                "is_favorite": bool(row["is_favorite"]),
                "tags": json.loads(row["tags"]) if row["tags"] else [],
                "notes": row["notes"]
            })
        
        return history_list
    
    def get_history_images(self, history_id: int, thumbnail_only: bool = False) -> List[Image.Image]:
        """
        履歴の画像を取得
        
        Args:
            history_id: 履歴ID
            thumbnail_only: サムネイルのみ取得
        
        Returns:
            画像のリスト
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT image_data, thumbnail_data, angle
            FROM history_images
            WHERE history_id = ?
            ORDER BY image_index
        """, (history_id,))
        
        rows = cursor.fetchall()
        
        images = []
        for row in rows:
            if thumbnail_only and row["thumbnail_data"]:
                img_data = row["thumbnail_data"]
            else:
                img_data = row["image_data"]
            
            img = Image.open(BytesIO(img_data))
            images.append(img)
        
        return images
    
    def toggle_favorite(self, history_id: int) -> bool:
        """
        お気に入りをトグル
        
        Args:
            history_id: 履歴ID
        
        Returns:
            新しいお気に入り状態
        """
        cursor = self.conn.cursor()
        
        # 現在の状態を取得
        cursor.execute(
            "SELECT is_favorite FROM generation_history WHERE id = ?",
            (history_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return False
        
        new_state = 0 if row["is_favorite"] else 1
        
        # 更新
        cursor.execute(
            "UPDATE generation_history SET is_favorite = ? WHERE id = ?",
            (new_state, history_id)
        )
        self.conn.commit()
        
        return bool(new_state)
    
    def update_tags(self, history_id: int, tags: List[str]):
        """
        タグを更新
        
        Args:
            history_id: 履歴ID
            tags: タグのリスト
        """
        cursor = self.conn.cursor()
        tags_json = json.dumps(tags, ensure_ascii=False)
        
        cursor.execute(
            "UPDATE generation_history SET tags = ? WHERE id = ?",
            (tags_json, history_id)
        )
        self.conn.commit()
    
    def update_notes(self, history_id: int, notes: str):
        """
        メモを更新
        
        Args:
            history_id: 履歴ID
            notes: メモ
        """
        cursor = self.conn.cursor()
        
        cursor.execute(
            "UPDATE generation_history SET notes = ? WHERE id = ?",
            (notes, history_id)
        )
        self.conn.commit()
    
    def delete_history(self, history_id: int):
        """
        履歴を削除
        
        Args:
            history_id: 履歴ID
        """
        cursor = self.conn.cursor()
        
        # 画像を削除
        cursor.execute("DELETE FROM history_images WHERE history_id = ?", (history_id,))
        
        # 履歴を削除
        cursor.execute("DELETE FROM generation_history WHERE id = ?", (history_id,))
        
        self.conn.commit()
        
        print(f"[History] 履歴削除: ID={history_id}")
    
    def get_statistics(self) -> Dict:
        """
        統計情報を取得
        
        Returns:
            統計情報の辞書
        """
        cursor = self.conn.cursor()
        
        # 総生成回数
        cursor.execute("SELECT COUNT(*) as count FROM generation_history")
        total_generations = cursor.fetchone()["count"]
        
        # 総画像数
        cursor.execute("SELECT COUNT(*) as count FROM history_images")
        total_images = cursor.fetchone()["count"]
        
        # お気に入り数
        cursor.execute("SELECT COUNT(*) as count FROM generation_history WHERE is_favorite = 1")
        favorite_count = cursor.fetchone()["count"]
        
        # 生成モード別
        cursor.execute("""
            SELECT generation_mode, COUNT(*) as count 
            FROM generation_history 
            GROUP BY generation_mode
        """)
        mode_counts = {row["generation_mode"]: row["count"] for row in cursor.fetchall()}
        
        return {
            "total_generations": total_generations,
            "total_images": total_images,
            "favorite_count": favorite_count,
            "mode_counts": mode_counts
        }
    
    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()


# テスト用
if __name__ == "__main__":
    from PIL import Image
    import numpy as np
    
    print("=" * 70)
    print("History Manager テスト")
    print("=" * 70)
    
    # テスト用データベース
    manager = HistoryManager("test_history.db")
    
    # ダミー画像を作成
    dummy_img = Image.new('RGB', (100, 100), color='red')
    
    # テストパラメータ
    test_params = {
        "gender": "female",
        "age_range": "20s",
        "pose": "front",
        "background": "white"
    }
    
    # 履歴を保存
    print("\n[TEST] 履歴を保存...")
    history_id = manager.save_generation(
        images=[dummy_img],
        parameters=test_params,
        generation_mode="variety",
        tags=["test", "red"],
        notes="テスト生成"
    )
    print(f"[OK] 保存完了: ID={history_id}")
    
    # 履歴リストを取得
    print("\n[TEST] 履歴リストを取得...")
    history_list = manager.get_history_list(limit=10)
    print(f"[OK] 履歴数: {len(history_list)}")
    for h in history_list:
        print(f"  - ID:{h['id']}, 日時:{h['created_at']}, 画像数:{h['num_images']}")
    
    # お気に入りをトグル
    print("\n[TEST] お気に入りをトグル...")
    is_favorite = manager.toggle_favorite(history_id)
    print(f"[OK] お気に入り: {is_favorite}")
    
    # 統計情報を取得
    print("\n[TEST] 統計情報を取得...")
    stats = manager.get_statistics()
    print(f"[OK] 総生成回数: {stats['total_generations']}")
    print(f"[OK] 総画像数: {stats['total_images']}")
    print(f"[OK] お気に入り数: {stats['favorite_count']}")
    
    manager.close()
    
    print("\n" + "=" * 70)
    print("[SUCCESS] すべてのテスト完了")
    print("=" * 70)


