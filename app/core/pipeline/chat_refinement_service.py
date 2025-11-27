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
        self.api_key = api_key  # APIキーを保存
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
        base_image: Image.Image = None,  # 修正対象の画像
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
            progress_callback("画像を編集しています...", 20)
        
        # AI応答メッセージを生成（シンプルに）
        ai_response = f"「{instruction}」を反映して画像を編集します。"
        changes = {"instruction": instruction}
        
        print(f"[Chat Refinement] 直接編集モード: 指示解析をスキップ")
        
        # 修正対象の画像がある場合は、それをGeminiに送信して編集
        if base_image:
            print(f"[Chat Refinement] 画像編集モード: 選択画像をベースに修正")
            
            # Geminiに画像を送信して編集指示（APIを1回だけ呼ぶ）
            images = await self._edit_with_gemini(
                base_image,
                instruction,
                changes,
                generate_service.adapter
            )
            metadata = {"method": "gemini_edit"}
        else:
            # 修正対象画像がない場合は再生成（ベースのmodel_attrsを使用）
            print(f"[Chat Refinement] 再生成モード: 1から生成")
            refined_config = copy.deepcopy(base_config)
            refined_config.num_outputs = 1  # 修正は1枚ずつ
            
            images, metadata = await generate_service.run(
                garments,
                base_model_attrs,
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
    
    async def _edit_with_gemini(
        self,
        base_image: Image.Image,
        instruction: str,
        changes: Dict,
        adapter
    ) -> List[Image.Image]:
        """Geminiを使用して画像を編集
        
        Args:
            base_image: 編集対象の画像
            instruction: ユーザーの指示
            changes: 変更内容
            adapter: Geminiアダプター
        
        Returns:
            編集された画像のリスト
        """
        import google.generativeai as genai
        
        print(f"[Chat Refinement] Geminiで画像編集: {instruction}")
        print(f"[Chat Refinement] 元の画像サイズ: {base_image.size}")
        
        try:
            # 画像をリサイズ（トークン数を削減）
            max_size = 1024
            if max(base_image.size) > max_size:
                ratio = max_size / max(base_image.size)
                new_size = tuple(int(dim * ratio) for dim in base_image.size)
                base_image = base_image.resize(new_size, Image.Resampling.LANCZOS)
                print(f"[Chat Refinement] リサイズ後: {base_image.size}")
            
            # RGBに変換（PNG等の形式問題を回避）
            if base_image.mode != 'RGB':
                base_image = base_image.convert('RGB')
                print(f"[Chat Refinement] RGBに変換")
            
            # APIキーを設定
            genai.configure(api_key=self.api_key)
            
            # 通常の画像生成と同じモデルを使用
            model = genai.GenerativeModel(model_name="gemini-3-pro-image-preview")
            
            # プロンプトを構築
            edit_prompt = f"""
Look at this image carefully.

This is a fashion photograph that needs to be edited.

USER INSTRUCTION: {instruction}

YOUR TASK:
Create a NEW version of this image with ONLY the following changes:
"""
            
            # 変更内容を追加
            for key, value in changes.items():
                if key == "pose":
                    edit_prompt += f"\n- Change the pose to: {value}"
                elif key == "background":
                    edit_prompt += f"\n- Change the background to: {value}"
                elif key == "lighting":
                    edit_prompt += f"\n- Adjust lighting: {value}"
                elif key == "expression":
                    edit_prompt += f"\n- Change expression: {value}"
                elif key == "prompt_additions":
                    edit_prompt += f"\n- {value}"
            
            edit_prompt += f"""

IMPORTANT:
- Keep the SAME PERSON (face, hair, body features)
- Keep the SAME CLOTHING (unless specifically asked to change)
- Only change what was requested
- Keep everything else exactly as it is in the original image
- Full body shot, professional photography
"""
            
            # 画像とプロンプトを送信
            prompt_parts = [base_image, edit_prompt]
            
            print(f"[Chat Refinement] Gemini編集プロンプト: {edit_prompt[:200]}...")
            
            response = model.generate_content(prompt_parts)
            
            # レスポンスから画像を取得
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                                from io import BytesIO
                                inline_data = part.inline_data
                                edited_image = Image.open(BytesIO(inline_data.data))
                                print(f"[Chat Refinement] 画像編集成功")
                                return [edited_image]
            
            print(f"[Chat Refinement] 画像が生成されませんでした")
            return []
        
        except Exception as e:
            print(f"[Chat Refinement] Gemini編集エラー: {e}")
            import traceback
            traceback.print_exc()
            return []


# テスト用
if __name__ == "__main__":
    import asyncio
    import os
    
    # 環境変数からAPIキーを取得
    TEST_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    if not TEST_API_KEY:
        print("環境変数 GEMINI_API_KEY を設定してください")
        exit(1)
    
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

