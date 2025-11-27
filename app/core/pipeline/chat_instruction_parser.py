"""Chat instruction parser using Gemini API"""

import google.generativeai as genai
from typing import Dict, List, Optional
import json


class ChatInstructionParser:
    """チャット指示を解析してパラメータ変更を抽出"""
    
    def __init__(self, api_key: str):
        """
        Args:
            api_key: Google Generative AI APIキー
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        # 通常の画像生成と同じモデルを使用（クォータ共有）
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def parse_instruction(
        self,
        instruction: str,
        current_params: Dict,
        conversation_history: List[Dict]
    ) -> Dict[str, any]:
        """
        ユーザーの指示を解析してパラメータ変更を抽出
        
        Args:
            instruction: ユーザーの指示文
            current_params: 現在のパラメータ
            conversation_history: 会話履歴
        
        Returns:
            変更すべきパラメータの辞書
        """
        # プロンプトを構築
        prompt = self._build_analysis_prompt(instruction, current_params, conversation_history)
        
        try:
            # Gemini APIで解析
            response = self.model.generate_content(prompt)
            
            # デバッグ: 生のレスポンスを出力
            print(f"[Chat Parser] Gemini生レスポンス:")
            print(f"{response.text[:500]}...")
            
            # レスポンスをパース
            modifications = self._parse_response(response.text)
            
            print(f"[Chat Parser] 解析結果: {modifications}")
            
            return modifications
        
        except Exception as e:
            print(f"[Chat Parser] エラー: {e}")
            # エラー時は最小限の変更を返す
            return {
                "prompt_additions": instruction,
                "ai_response": f"「{instruction}」という指示を反映して画像を再生成します。"
            }
    
    def _build_analysis_prompt(
        self,
        instruction: str,
        current_params: Dict,
        conversation_history: List[Dict]
    ) -> str:
        """解析用プロンプトを構築"""
        
        # 会話履歴を文字列化
        history_text = ""
        for msg in conversation_history[-5:]:  # 直近5件
            sender = "ユーザー" if msg["sender"] == "user" else "AI"
            history_text += f"{sender}: {msg['message']}\n"
        
        prompt = f"""
あなたはファッションモデル画像生成AIのアシスタントです。
ユーザーが生成された画像に対して修正指示を出しています。

【会話履歴】
{history_text}

【ユーザーの新しい指示】
{instruction}

【現在のパラメータ】
- 性別: {current_params.get('gender', 'female')}
- 年代: {current_params.get('age_range', '20s')}
- 地域: {current_params.get('ethnicity', 'asian')}
- 体型: {current_params.get('body_type', 'standard')}
- ポーズ: {current_params.get('pose', 'front')}
- 背景: {current_params.get('background', 'white')}

【あなたのタスク】
ユーザーの指示を分析して、以下のJSON形式で変更内容を返してください：

{{
  "changes": {{
    "gender": "male または female (変更がない場合はnull)",
    "age_range": "10s/20s/30s/40s/50s+ (変更がない場合はnull)",
    "body_type": "slim/standard/athletic/plus-size (変更がない場合はnull)",
    "pose": "ポーズの変更 (変更がない場合はnull)",
    "background": "背景の変更 (変更がない場合はnull)",
    "lighting": "明るさや照明の指示 (変更がない場合はnull)",
    "expression": "表情の指示 (変更がない場合はnull)",
    "prompt_additions": "プロンプトに追加すべき指示文"
  }},
  "ai_response": "ユーザーへの返答メッセージ（日本語、フレンドリーに）"
}}

【重要な指示】
- JSONのみを返してください（説明文は不要）
- 変更がないパラメータはnullにしてください
- 曖昧な指示の場合は、最も一般的な解釈を選んでください
- ai_responseには、何を変更するかを明確に伝えてください

それでは、JSON形式で回答してください：
"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, any]:
        """Geminiのレスポンスをパース"""
        try:
            # JSONブロックを抽出（```json ... ``` の場合に対応）
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text.strip()
            
            # JSONをパース
            parsed = json.loads(json_text)
            
            # 変更内容を抽出
            changes = parsed.get("changes", {})
            ai_response = parsed.get("ai_response", "画像を再生成します。")
            
            # nullを除去
            modifications = {
                "changes": {k: v for k, v in changes.items() if v is not None},
                "ai_response": ai_response
            }
            
            return modifications
        
        except Exception as e:
            print(f"[Chat Parser] JSONパースエラー: {e}")
            print(f"[Chat Parser] レスポンス: {response_text}")
            
            # フォールバック: プロンプトに直接追加
            return {
                "changes": {
                    "prompt_additions": response_text[:200]  # 最初の200文字
                },
                "ai_response": "指示を反映して画像を再生成します。"
            }
    
    def apply_modifications(
        self,
        base_params: Dict,
        modifications: Dict
    ) -> Dict:
        """修正内容をパラメータに適用
        
        Args:
            base_params: ベースパラメータ
            modifications: 修正内容
        
        Returns:
            更新されたパラメータ
        """
        updated_params = base_params.copy()
        changes = modifications.get("changes", {})
        
        print(f"[Chat Parser] apply_modifications - 入力changes: {changes}")
        
        # 各パラメータを更新
        for key, value in changes.items():
            if value is not None:
                print(f"[Chat Parser] パラメータ更新: {key} = {value}")
                
                if key == "prompt_additions":
                    # カスタム説明に追加
                    existing_desc = updated_params.get("custom_description", "")
                    updated_params["custom_description"] = f"{existing_desc} {value}".strip()
                    print(f"[Chat Parser] custom_description更新: {updated_params['custom_description']}")
                elif key in ["lighting", "expression"]:
                    # カスタム説明に追加
                    existing_desc = updated_params.get("custom_description", "")
                    updated_params["custom_description"] = f"{existing_desc} {key}: {value}".strip()
                    print(f"[Chat Parser] custom_description更新({key}): {updated_params['custom_description']}")
                else:
                    # 直接パラメータを更新
                    updated_params[key] = value
        
        print(f"[Chat Parser] apply_modifications - 出力params: {updated_params}")
        
        return updated_params


# テスト用
if __name__ == "__main__":
    import os
    
    # 環境変数からAPIキーを取得
    TEST_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    if not TEST_API_KEY:
        print("環境変数 GEMINI_API_KEY を設定してください")
        exit(1)
    
    parser = ChatInstructionParser(TEST_API_KEY)
    
    # テストケース
    test_instructions = [
        "もっと明るくして",
        "背景を青空に変更",
        "笑顔にして",
        "もっとカジュアルな雰囲気で"
    ]
    
    current_params = {
        "gender": "female",
        "age_range": "20s",
        "ethnicity": "asian",
        "body_type": "standard",
        "pose": "front",
        "background": "white"
    }
    
    print("=" * 70)
    print("Chat Instruction Parser テスト")
    print("=" * 70)
    
    for instruction in test_instructions:
        print(f"\n[テスト] 指示: {instruction}")
        
        try:
            result = parser.parse_instruction(instruction, current_params, [])
            print(f"[結果] 変更内容: {result['changes']}")
            print(f"[結果] AI応答: {result['ai_response']}")
        except Exception as e:
            print(f"[エラー] {e}")


