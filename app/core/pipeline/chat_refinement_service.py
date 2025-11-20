"""Chat-based image refinement service"""

import copy
import sys
from typing import Dict, List, Tuple, Optional
from PIL import Image
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.models.clothing_item import ClothingItem
from app.models.model_attributes import ModelAttributes
from app.models.generation_config import GenerationConfig
from app.core.pipeline.chat_instruction_parser import ChatInstructionParser


class ChatRefinementService:
    """チャットベースの画像修正サービス"""
    
    def __init__(self, api_key: str):
        """
        Args:
            api_key: Gemini APIキー
        """
        self.parser = ChatInstructionParser(api_key)
        self.refinement_history: List[Dict] = []
    
    async def refine_image(
        self,
        instruction: str,
        generate_service,
        garments: List[ClothingItem],
        base_model_attrs: ModelAttributes,
        base_config: GenerationConfig,
        conversation_history: List[Dict],
        progress_callback=None
    ) -> Tuple[List[Image.Image], str, Dict]:
        """
        チャット指示に基づいて画像を修正
        
        Args:
            instruction: ユーザーの修正指示
            generate_service: GenerateServiceインスタンス
            garments: 衣類アイテムのリスト
            base_model_attrs: ベースモデル属性
            base_config: ベース生成設定
            conversation_history: 会話履歴
            progress_callback: 進捗コールバック
        
        Returns:
            (生成画像リスト, AI応答メッセージ, メタデータ)
        """
        print(f"\n[Chat Refinement] ユーザー指示: {instruction}")
        
        # 進捗報告
        if progress_callback:
            progress_callback("指示を解析しています...", 10)
        
        # 現在のパラメータを辞書化
        current_params = {
            "gender": base_model_attrs.gender,
            "age_range": base_model_attrs.age_range,
            "ethnicity": base_model_attrs.ethnicity,
            "body_type": base_model_attrs.body_type,
            "pose": base_model_attrs.pose,
            "background": base_model_attrs.background,
            "custom_description": base_model_attrs.custom_description or ""
        }
        
        # 指示を解析
        modifications = self.parser.parse_instruction(
            instruction,
            current_params,
            conversation_history
        )
        
        ai_response = modifications.get("ai_response", "画像を再生成します。")
        changes = modifications.get("changes", {})
        
        print(f"[Chat Refinement] 変更内容: {changes}")
        print(f"[Chat Refinement] AI応答: {ai_response}")
        
        # 進捗報告
        if progress_callback:
            progress_callback("パラメータを更新しています...", 20)
        
        # パラメータを更新
        updated_params = self.parser.apply_modifications(current_params, modifications)
        
        # 新しいModelAttributesを作成
        refined_model_attrs = ModelAttributes(
            gender=updated_params.get("gender", base_model_attrs.gender),
            age_range=updated_params.get("age_range", base_model_attrs.age_range),
            ethnicity=updated_params.get("ethnicity", base_model_attrs.ethnicity),
            body_type=updated_params.get("body_type", base_model_attrs.body_type),
            height=updated_params.get("height", base_model_attrs.height),
            pose=updated_params.get("pose", base_model_attrs.pose),
            background=updated_params.get("background", base_model_attrs.background),
            custom_description=updated_params.get("custom_description", "")
        )
        
        # 進捗報告
        if progress_callback:
            progress_callback("画像を再生成しています...", 30)
        
        # 画像を再生成
        refined_config = copy.deepcopy(base_config)
        refined_config.num_outputs = 1  # 修正は1枚ずつ
        
        images, metadata = await generate_service.run(
            garments,
            refined_model_attrs,
            refined_config
        )
        
        # 修正履歴に追加
        self.refinement_history.append({
            "instruction": instruction,
            "changes": changes,
            "ai_response": ai_response,
            "result": "success" if images else "failed"
        })
        
        # メタデータに修正情報を追加
        metadata["refinement"] = {
            "instruction": instruction,
            "changes": changes,
            "history_count": len(self.refinement_history)
        }
        
        return images, ai_response, metadata
    
    def get_refinement_history(self) -> List[Dict]:
        """修正履歴を取得"""
        return self.refinement_history.copy()
    
    def clear_history(self):
        """履歴をクリア"""
        self.refinement_history = []


# テスト用
if __name__ == "__main__":
    import asyncio
    
    # テスト用APIキー
    TEST_API_KEY = "AIzaSyDLQVe0L5jn6R7lJNV4coe5FY-ICRHtSIg"
    
    service = ChatRefinementService(TEST_API_KEY)
    
    # テストケース
    test_instruction = "もっと明るくして、笑顔にしてください"
    
    current_params = {
        "gender": "female",
        "age_range": "20s",
        "ethnicity": "asian",
        "body_type": "standard",
        "pose": "front",
        "background": "white"
    }
    
    print("=" * 70)
    print("Chat Refinement Service テスト")
    print("=" * 70)
    print(f"\n[テスト] 指示: {test_instruction}")
    
    # 指示を解析（同期版テスト）
    modifications = service.parser.parse_instruction(
        test_instruction,
        current_params,
        []
    )
    
    print(f"\n[結果] 変更内容: {modifications['changes']}")
    print(f"[結果] AI応答: {modifications['ai_response']}")

