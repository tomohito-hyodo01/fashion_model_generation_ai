"""Batch processing for multiple garments"""

import asyncio
import sys
from typing import List, Dict, Tuple, Callable, Optional
from PIL import Image
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.models.clothing_item import ClothingItem
from app.models.model_attributes import ModelAttributes
from app.models.generation_config import GenerationConfig


class BatchProcessor:
    """バッチ処理エンジン
    
    複数の衣類を自動的に処理します
    """
    
    def __init__(self):
        """初期化"""
        self.is_cancelled = False
    
    async def process_batch(
        self,
        generate_service,
        garment_groups: List[List[ClothingItem]],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
        progress_callback: Optional[Callable] = None
    ) -> List[Tuple[List[Image.Image], Dict]]:
        """
        バッチ処理を実行
        
        Args:
            generate_service: GenerateServiceインスタンス
            garment_groups: 衣類グループのリスト（各グループが1回の生成）
            model_attrs: モデル属性
            config: 生成設定
            progress_callback: 進捗コールバック
        
        Returns:
            (生成画像, メタデータ)のリスト
        """
        results = []
        total_groups = len(garment_groups)
        
        print(f"\n[Batch] バッチ処理開始: {total_groups}グループ")
        
        for i, garments in enumerate(garment_groups):
            if self.is_cancelled:
                print("[Batch] キャンセルされました")
                break
            
            print(f"\n[Batch] グループ {i+1}/{total_groups} を処理中...")
            
            # 進捗報告
            if progress_callback:
                progress = int((i / total_groups) * 100)
                progress_callback(f"グループ {i+1}/{total_groups} を生成中...", progress)
            
            try:
                # 生成実行
                images, metadata = await generate_service.run(
                    garments,
                    model_attrs,
                    config
                )
                
                results.append((images, metadata))
                print(f"[Batch] グループ {i+1} 完了: {len(images)}枚生成")
            
            except Exception as e:
                print(f"[Batch] グループ {i+1} でエラー: {e}")
                # エラーでも続行
                results.append(([], {"error": str(e)}))
        
        # 最終進捗
        if progress_callback:
            progress_callback("バッチ処理完了", 100)
        
        print(f"\n[Batch] バッチ処理完了: {len(results)}/{total_groups}グループ成功")
        
        return results
    
    def cancel(self):
        """バッチ処理をキャンセル"""
        self.is_cancelled = True
        print("[Batch] キャンセル要求を受信")
    
    def load_garments_from_directory(
        self,
        directory: str,
        clothing_type: str = "TOP"
    ) -> List[ClothingItem]:
        """
        ディレクトリから衣類画像を一括読み込み
        
        Args:
            directory: ディレクトリパス
            clothing_type: 衣類タイプ（デフォルト: TOP）
        
        Returns:
            ClothingItemのリスト
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            print(f"[Batch] ディレクトリが見つかりません: {directory}")
            return []
        
        # 画像ファイルを取得
        image_extensions = [".png", ".jpg", ".jpeg", ".webp"]
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(dir_path.glob(f"*{ext}"))
            image_files.extend(dir_path.glob(f"*{ext.upper()}"))
        
        # ClothingItemを作成
        garments = []
        for img_file in image_files:
            try:
                garment = ClothingItem(
                    image_path=str(img_file),
                    clothing_type=clothing_type,
                    colors=[],
                    analyzed_description=f"{clothing_type.lower()} garment from {img_file.name}"
                )
                garments.append(garment)
                print(f"[Batch] 読み込み: {img_file.name}")
            except Exception as e:
                print(f"[Batch] 読み込みエラー({img_file.name}): {e}")
        
        print(f"[Batch] {len(garments)}枚の衣類を読み込みました")
        
        return garments
    
    def create_combinations(
        self,
        tops: List[ClothingItem],
        bottoms: List[ClothingItem]
    ) -> List[List[ClothingItem]]:
        """
        トップスとボトムスの組み合わせを作成
        
        Args:
            tops: トップスのリスト
            bottoms: ボトムスのリスト
        
        Returns:
            組み合わせのリスト
        """
        combinations = []
        
        for top in tops:
            for bottom in bottoms:
                combinations.append([top, bottom])
        
        print(f"[Batch] {len(combinations)}個の組み合わせを作成しました")
        
        return combinations


# テスト用
if __name__ == "__main__":
    print("=" * 70)
    print("Batch Processor テスト")
    print("=" * 70)
    
    processor = BatchProcessor()
    
    # ダミー衣類を作成
    print("\n[TEST] ダミー衣類を作成...")
    from PIL import Image
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # ダミー画像を作成
        for i in range(3):
            img = Image.new('RGB', (100, 100), color=['red', 'blue', 'green'][i])
            img_path = os.path.join(temp_dir, f"garment_{i+1}.png")
            img.save(img_path)
        
        # ディレクトリから読み込み
        print(f"\n[TEST] ディレクトリから読み込み: {temp_dir}")
        garments = processor.load_garments_from_directory(temp_dir, "TOP")
        print(f"[OK] {len(garments)}枚読み込み")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] すべてのテスト完了")
    print("=" * 70)

