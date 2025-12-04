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
        from google import genai
        from google.genai import types

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

            # 新しいSDK（google-genai）を使用
            client = genai.Client(api_key=self.api_key)

            # プロンプトを構築 - 元画像の維持を明確に指示
            edit_prompt = f"""
Make a minor edit to this photograph.

USER REQUEST: {instruction}

STRICT REQUIREMENTS:
1. Keep the EXACT same person (identical face and body)
2. Keep the EXACT same outfit (same clothes, same style, same colors)
3. Keep the EXACT same pose and body position
4. Keep the EXACT same camera angle
5. Apply ONLY the change requested above - nothing else

Output the edited photograph.
"""

            print(f"[Chat Refinement] Gemini編集プロンプト: {edit_prompt[:200]}...")

            # 画像をバイト列に変換
            from io import BytesIO
            img_buffer = BytesIO()
            base_image.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()

            print(f"[Chat Refinement] Gemini APIを呼び出し中...")

            # Gemini 3 Pro Imageで画像編集
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                    edit_prompt
                ],
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"]
                )
            )

            print(f"[Chat Refinement] Gemini APIレスポンス受信")

            # レスポンスから画像を取得
            if response.candidates:
                print(f"[Chat Refinement] candidates数: {len(response.candidates)}")
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.inline_data and part.inline_data.data:
                                edited_image = Image.open(BytesIO(part.inline_data.data))
                                print(f"[Chat Refinement] 画像編集成功")
                                return [edited_image]

            print(f"[Chat Refinement] 画像が生成されませんでした")
            print(f"[Chat Refinement] response: {response}")
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

