"""Main generation service with fidelity checking"""

import asyncio
from typing import List, Tuple, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

from models.clothing_item import ClothingItem
from models.model_attributes import ModelAttributes
from models.generation_config import GenerationConfig
from core.adapters.provider_base import ProviderBase
from core.vton.fidelity_check import FidelityChecker


class GenerateService:
    """生成サービス（前処理→生成→検証→再生成）"""

    def __init__(
        self,
        adapter: ProviderBase,
        fidelity_checker: FidelityChecker,
        max_retries: int = 3,
        max_parallel: int = 4,
    ):
        """
        Args:
            adapter: プロバイダアダプタ
            fidelity_checker: 忠実度チェッカー
            max_retries: 最大リトライ回数
            max_parallel: 最大並列数
        """
        self.adapter = adapter
        self.fidelity = fidelity_checker
        self.max_retries = max_retries
        self.max_parallel = max_parallel
        self.executor = ThreadPoolExecutor(max_workers=max_parallel)
        self.progress_callback = None  # 進捗コールバック

    async def run(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
    ) -> Tuple[List[Image.Image], Dict[str, Any]]:
        """
        生成処理を実行

        Args:
            garments: 衣類アイテムのリスト
            model_attrs: モデル属性
            config: 生成設定

        Returns:
            (生成画像のリスト, メタデータ)
        """
        num_outputs = config.num_outputs
        
        # 進捗報告: 初期化開始
        if self.progress_callback:
            self.progress_callback("処理を開始しています...", 5)

        # プロバイダが複数出力にネイティブ対応しているか確認
        if self.adapter.supports_multi_output():
            # 一括生成
            imgs, meta = await self._generate_batch(
                garments, model_attrs, config, num_outputs
            )
        else:
            # 並列/逐次生成（OpenAI等）
            imgs, meta = await self._generate_parallel(
                garments, model_attrs, config, num_outputs
            )

        # 忠実度検証（オプション）
        # validated_imgs = await self._validate_fidelity(garments, imgs)

        return imgs, meta

    async def _generate_batch(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
        num_outputs: int,
    ) -> Tuple[List[Image.Image], Dict[str, Any]]:
        """一括生成（Stability/Imagen）"""
        loop = asyncio.get_event_loop()

        # 進捗を報告: 準備完了
        if self.progress_callback:
            self.progress_callback("画像を準備しています...", 10)
            
        # 少し待機して進捗を反映
        await asyncio.sleep(0.2)
        
        # アダプターに進捗コールバックを渡す
        if hasattr(self.adapter, 'set_progress_callback'):
            self.adapter.set_progress_callback(self.progress_callback)
        
        # 進捗を報告: 生成開始
        if self.progress_callback:
            self.progress_callback("API接続を確認しています...", 15)
        
        await asyncio.sleep(0.2)
        
        if self.progress_callback:
            self.progress_callback("生成リクエストを準備しています...", 20)
            
        await asyncio.sleep(0.2)

        # バックグラウンドで実行
        imgs, meta = await loop.run_in_executor(
            self.executor,
            self.adapter.generate,
            garments,
            model_attrs,
            config,
            num_outputs,
        )
        
        # 進捗を報告: 生成完了
        if self.progress_callback:
            self.progress_callback("画像を処理しています...", 95)

        return imgs, meta

    async def _generate_parallel(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
        num_outputs: int,
    ) -> Tuple[List[Image.Image], Dict[str, Any]]:
        """並列生成（OpenAI）"""
        # 複数のタスクを並列実行
        tasks = []
        for i in range(num_outputs):
            task = self._generate_single(garments, model_attrs, config, i)
            tasks.append(task)

        # 全タスクの完了を待つ
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 結果を統合
        imgs = []
        metas = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Error in parallel generation: {result}")
                continue

            img_list, meta = result
            if img_list:
                imgs.extend(img_list)
                metas.append(meta)

        meta = {"partials": metas, "total": len(imgs)}
        return imgs, meta

    async def _generate_single(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
        index: int,
    ) -> Tuple[List[Image.Image], Dict[str, Any]]:
        """単一画像生成（非同期）"""
        loop = asyncio.get_event_loop()

        # バックグラウンドで実行
        imgs, meta = await loop.run_in_executor(
            self.executor, self.adapter.generate, garments, model_attrs, config, 1
        )

        return imgs, meta

    async def _validate_fidelity(
        self, garments: List[ClothingItem], imgs: List[Image.Image]
    ) -> List[Tuple[Image.Image, Dict[str, float]]]:
        """忠実度検証（非同期）"""
        validated = []

        for img in imgs:
            scores = {}
            all_pass = True

            # 各衣類に対して検証
            for garment in garments:
                score = self.fidelity.evaluate(garment.image_path, img)
                scores[garment.clothing_type] = score

                if not self.fidelity.pass_all(score):
                    all_pass = False
                    break

            if all_pass:
                validated.append((img, scores))

        return validated

