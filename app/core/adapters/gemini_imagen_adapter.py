"""Google Generative AI (google-generativeai) Imagen 4 adapter"""

from io import BytesIO
from typing import List, Tuple, Dict, Any, Optional
from PIL import Image
from pathlib import Path
import google.generativeai as genai
import sys

# プロジェクトルートをパスに追加（スタンドアロン実行時のため）
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))

from models.clothing_item import ClothingItem
from models.model_attributes import ModelAttributes
from models.generation_config import GenerationConfig
from core.adapters.provider_base import ProviderBase


class GeminiImagenAdapter(ProviderBase):
    """Google Generative AI - Gemini 3 Pro Image Generation アダプタ"""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: Google AI Studio APIキー
        """
        super().__init__(api_key)
        
        # APIキーの設定
        genai.configure(api_key=api_key)
        
        # Gemini 3 Pro Image（最新の画像生成モデル）
        self.model_name = "gemini-3-pro-image-preview"
        
        # 進捗コールバック
        self.progress_callback = None
        
        # 参考人物画像（オプション）
        self.reference_person_image: Optional[str] = None
        
        # カスタム背景画像（オプション）
        self.custom_background_image: Optional[str] = None
    
    def set_reference_person(self, image_path: Optional[str]):
        """参考人物画像を設定
        
        Args:
            image_path: 参考人物画像のパス（Noneの場合はクリア）
        """
        self.reference_person_image = image_path
        if image_path:
            print(f"[Gemini Adapter] ★参考人物画像を設定★: {Path(image_path).name}")
            print(f"[Gemini Adapter] フルパス: {image_path}")
        else:
            print("[Gemini Adapter] 参考人物画像をクリア")
    
    def set_custom_background(self, image_path: Optional[str]):
        """カスタム背景画像を設定
        
        Args:
            image_path: 背景画像のパス（Noneの場合はクリア）
        """
        self.custom_background_image = image_path
        if image_path:
            print(f"[Gemini Adapter] ★カスタム背景画像を設定★: {Path(image_path).name}")
        else:
            print("[Gemini Adapter] カスタム背景画像をクリア")
    
    def set_progress_callback(self, callback):
        """進捗コールバック関数を設定"""
        self.progress_callback = callback

    def prepare(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
    ) -> Dict[str, Any]:
        """生成リクエストの準備（Imagen 4）"""
        from core.pipeline.prompt_generator import PromptGenerator

        generator = PromptGenerator()
        prompts = generator.build_faithful_prompt(garments, model_attrs, config)

        # アスペクト比を決定
        aspect_ratio = self._size_to_aspect_ratio(config.size)

        # Imagen 4のパラメータ
        return {
            "prompt": prompts["prompt"],
            "numberOfImages": config.num_outputs,  # 1-4枚を直接指定可能
            "aspectRatio": aspect_ratio,
            "safetyFilterLevel": "block_low_and_above",  # block_low_and_above (Imagenのデフォルト)
            "personGeneration": "allow_adult",  # dont_allow/allow_adult/allow_all
        }

    def _size_to_aspect_ratio(self, size: str) -> str:
        """サイズからアスペクト比を決定"""
        if size == "1024x1024":
            return "1:1"
        elif size == "1024x1792":
            return "9:16"
        elif size == "1792x1024":
            return "16:9"
        else:
            return "1:1"

    def generate(
        self,
        garments: List[ClothingItem],
        model_attrs: ModelAttributes,
        config: GenerationConfig,
        num_outputs: int,
        reference_person_image: Optional[str] = None,
    ) -> Tuple[List[Image.Image], Dict[str, Any]]:
        """
        画像生成（Gemini 3 Pro Image - Virtual Try-On）

        Args:
            garments: 衣類アイテムのリスト
            model_attrs: モデル属性
            config: 生成設定
            num_outputs: 出力枚数（1-4）
            reference_person_image: 参考人物画像のパス（オプション）

        Returns:
            (生成画像のリスト, メタデータ)
        """
        params = self.prepare(garments, model_attrs, config)

        try:
            # 進捗報告: APIキー確認
            if self.progress_callback:
                self.progress_callback("API接続を確認しています...", 25)
            
            # 進捗報告: モデル初期化
            if self.progress_callback:
                self.progress_callback("Geminiモデルを初期化しています...", 30)
            
            model = genai.GenerativeModel(model_name="gemini-3-pro-image-preview")
            
            generated_images = []
            
            # 各出力に対して処理
            for i in range(num_outputs):
                print(f"\n=== Generating image {i+1}/{num_outputs} ===")
                
                # 進捗計算: 35% + (55% * 進捗) = 35%～90%の範囲で分配
                base_progress = 35
                step_size = 55
                step_progress = int(step_size * i / num_outputs)
                current_progress = base_progress + step_progress
                
                if self.progress_callback:
                    self.progress_callback(f"画像 {i+1}/{num_outputs} の生成準備中...", current_progress)
                
                # ポーズと背景の詳細な説明
                pose_descriptions = {
                    # 元々のポーズ
                    "front": "standing straight facing the camera with both feet on the ground",
                    "side": "standing in profile view showing the side of the body",
                    "walking": "walking naturally with one leg forward in motion",
                    "sitting": "sitting on a chair or bench with legs positioned naturally, full body visible including feet",
                    # Phase 1で追加したポーズ
                    "arms_crossed": "standing with arms crossed, confident pose",
                    "hands_on_hips": "standing with hands on hips, assertive pose",
                    "casual": "relaxed casual pose, one hand in pocket",
                    "professional": "professional formal pose, standing upright",
                    # Phase 2で追加した角度ポーズ
                    "three_quarter_front": "standing at three-quarter front view, 45 degrees angle",
                    "three_quarter_back": "standing at three-quarter back view, 135 degrees angle",
                    "back": "standing facing away from camera, back view",
                    "three_quarter_front_left": "standing at three-quarter front view from left",
                    "side_left": "standing in profile view from left side",
                    # カスタムポーズ
                    "custom": model_attrs.custom_description if model_attrs.custom_description else "natural standing pose"
                }
                
                background_descriptions = {
                    # 元々の背景
                    "white": "plain solid white background, studio setting",
                    "transparent": "solid white background",
                    "studio": "professional photo studio background with soft lighting",
                    "location": "outdoor or indoor location setting",
                    # Phase 1で追加した背景
                    "gray": "neutral gray background, professional look",
                    "city": "modern city street background, urban setting",
                    "nature": "natural outdoor setting with trees and greenery",
                    "beach": "beach background with sand and ocean",
                    "indoor": "indoor interior background, modern room",
                    "abstract": "abstract artistic background with soft colors",
                    # カスタム背景
                    "custom": "custom background setting"
                }
                
                # ポーズと背景の説明を取得
                # custom_descriptionがある場合はそれを優先
                if model_attrs.custom_description and ("Pose:" in model_attrs.custom_description):
                    # custom_descriptionからポーズ部分を抽出
                    pose_desc = model_attrs.custom_description.split("Pose:")[1].split(".")[0].strip() if "Pose:" in model_attrs.custom_description else pose_descriptions.get(model_attrs.pose, "standing naturally")
                else:
                    pose_desc = pose_descriptions.get(model_attrs.pose, "standing naturally")
                
                if model_attrs.custom_description and ("Background:" in model_attrs.custom_description):
                    # custom_descriptionから背景部分を抽出
                    bg_desc = model_attrs.custom_description.split("Background:")[1].split(".")[0].strip() if "Background:" in model_attrs.custom_description else background_descriptions.get(model_attrs.background, "plain white background")
                else:
                    bg_desc = background_descriptions.get(model_attrs.background, "plain white background")
                
                # デバッグ: 選択されたポーズと背景を出力
                print(f"  Selected pose: {model_attrs.pose} → {pose_desc}")
                print(f"  Selected background: {model_attrs.background} → {bg_desc}")
                if model_attrs.custom_description:
                    print(f"  Custom description: {model_attrs.custom_description}")
                
                # 進捗報告: 画像読み込み開始
                read_progress = current_progress + int(step_size * 0.1 / num_outputs)
                if self.progress_callback:
                    self.progress_callback(f"服の画像を読み込んでいます ({i+1}/{num_outputs})...", read_progress)
                
                # 画像を入力として追加
                prompt_parts = []
                garment_count = 0
                has_reference_person = False
                
                # 参考人物画像がある場合は最初に追加（self.reference_person_imageを使用）
                print(f"  [DEBUG] self.reference_person_image = {self.reference_person_image}")
                if self.reference_person_image:
                    try:
                        person_img = Image.open(self.reference_person_image)
                        
                        # 画像サイズを制限（大きすぎるとエラーになる可能性）
                        max_size = 1024
                        if max(person_img.size) > max_size:
                            ratio = max_size / max(person_img.size)
                            new_size = tuple(int(dim * ratio) for dim in person_img.size)
                            person_img = person_img.resize(new_size, Image.Resampling.LANCZOS)
                            print(f"  Resized reference person image to: {new_size}")
                        
                        # RGBに変換（webp等の形式問題を回避）
                        person_img = person_img.convert('RGB')
                        
                        prompt_parts.append(person_img)
                        has_reference_person = True
                        print(f"  ★★★ Added reference person image: {Path(self.reference_person_image).name} ★★★")
                        print(f"  ★ MODE: 参考人物に服を着せるモード ★")
                    except Exception as e:
                        print(f"  ❌ Warning: Could not load reference person image: {e}")
                else:
                    print(f"  ℹ️ No reference person image (will generate new model)")
                
                # 衣類画像を追加
                for garment in garments:
                    try:
                        # PIL Imageとして読み込み
                        garment_image = Image.open(garment.image_path)
                        prompt_parts.append(garment_image)
                        garment_count += 1
                        print(f"  Added garment image: {garment.display_name}")
                    except Exception as e:
                        print(f"  Warning: Could not load garment image {garment.image_path}: {e}")
                
                # カスタム背景画像を追加
                has_custom_background = False
                if self.custom_background_image:
                    try:
                        bg_img = Image.open(self.custom_background_image)
                        # 画像サイズを制限
                        max_size = 1024
                        if max(bg_img.size) > max_size:
                            ratio = max_size / max(bg_img.size)
                            new_size = tuple(int(dim * ratio) for dim in bg_img.size)
                            bg_img = bg_img.resize(new_size, Image.Resampling.LANCZOS)
                        bg_img = bg_img.convert('RGB')
                        prompt_parts.append(bg_img)
                        has_custom_background = True
                        print(f"  ★ Added custom background image: {Path(self.custom_background_image).name} ★")
                    except Exception as e:
                        print(f"  Warning: Could not load custom background image: {e}")
                
                # 進捗報告: プロンプト構築
                prompt_progress = current_progress + int(step_size * 0.2 / num_outputs)
                if self.progress_callback:
                    self.progress_callback(f"プロンプトを構築しています ({i+1}/{num_outputs})...", prompt_progress)
                
                # プロンプトの構築（参考人物の有無で分岐）
                if has_reference_person:
                    # 参考人物がいる場合: その人物に服を着せる
                    prompt_text = (
                        f"IMAGE 1 shows a PERSON (the reference person).\n"
                        f"IMAGES 2-{garment_count+1} show CLOTHING items.\n"
                        f"\n"
                        f"YOUR TASK:\n"
                        f"Generate a photograph of THE EXACT SAME PERSON from image 1, but dressed in the clothing from images 2-{garment_count+1}.\n"
                        f"\n"
                        f"CRITICAL REQUIREMENTS:\n"
                        f"1. FACE: Use the EXACT SAME face from image 1 - same eyes, nose, mouth, facial structure, skin tone\n"
                        f"2. HAIR: Use the EXACT SAME hair from image 1 - same color, style, length\n"
                        f"3. BODY: Use the EXACT SAME body type from image 1 - same height, build, proportions\n"
                        f"4. CLOTHING: Replace ONLY the clothing with the items from images 2-{garment_count+1}\n"
                        f"5. Copy the clothing exactly - same colors, patterns, textures, logos\n"
                        f"\n"
                        f"CLOTHING FIT - EXTREMELY IMPORTANT:\n"
                        f"- The clothing MUST fit naturally and snugly on the person's body.\n"
                        f"- The fabric should follow the body contours perfectly - NOT floating or loose.\n"
                        f"- Show realistic wrinkles and folds where the fabric touches the body.\n"
                        f"- NO air gaps between clothing and body.\n"
                        f"- NO baggy, oversized, or ill-fitting appearance.\n"
                        f"- The garment should look like it was tailored specifically for this person.\n"
                        f"- Sleeves should fit arms snugly, pants should fit legs properly.\n"
                        f"\n"
                        f"IMPORTANT: This is NOT a new person. This is THE PERSON FROM IMAGE 1 wearing different clothes.\n"
                        f"Think of it as: Take person from image 1 → Change only their clothes → That's the result.\n"
                        f"\n"
                        f"Pose: {pose_desc}\n"
                        f"Background: {bg_desc}\n"
                        f"Style: Professional fashion photography, full body shot\n"
                    )
                else:
                    # 参考人物がいない場合: 新しいモデルを生成（従来通り）
                    # カスタム背景画像がある場合の背景指示
                    if has_custom_background:
                        bg_instruction = f"Use the LAST image as the background. Place the model in front of this exact background scene."
                        image_count = garment_count + 1
                    else:
                        bg_instruction = f"BACKGROUND: {bg_desc}."
                        image_count = garment_count
                    
                    prompt_text = (
                        f"CRITICAL INSTRUCTIONS:\n"
                        f"1. Look at the {garment_count} clothing reference image(s) above.\n"
                        f"2. Create a photograph of a {model_attrs.age_range} {model_attrs.ethnicity} {model_attrs.gender} fashion model.\n"
                        f"3. The model MUST wear the EXACT SAME clothing items from the reference images.\n"
                        f"4. PRESERVE ALL DETAILS: exact colors (RGB values), patterns, textures, logos, text, prints, buttons, zippers.\n"
                        f"5. DO NOT change, modify, or redesign the clothing. Copy it exactly as shown.\n"
                        f"6. POSE: The model is {pose_desc}.\n"
                        f"7. {bg_instruction}\n"
                        f"8. FRAMING: Full body shot showing the model from head to toe.\n"
                        f"9. LIGHTING: Professional studio lighting, even and natural.\n"
                        f"10. STYLE: Photorealistic, high-resolution professional fashion photography.\n"
                        f"\n"
                        f"CLOTHING FIT - EXTREMELY IMPORTANT:\n"
                        f"- The clothing MUST fit naturally and snugly on the model's body.\n"
                        f"- The fabric should follow the body contours perfectly - NOT floating or loose.\n"
                        f"- Show realistic wrinkles and folds where the fabric touches the body.\n"
                        f"- NO air gaps between clothing and body.\n"
                        f"- NO baggy, oversized, or ill-fitting appearance.\n"
                        f"- The garment should look like it was tailored specifically for this model's body type ({model_attrs.body_type}).\n"
                        f"- Sleeves should fit arms snugly, pants should fit legs properly.\n"
                        f"\n"
                        f"Body type: {model_attrs.body_type}. "
                        f"IMPORTANT: The clothing items in the reference images are the PRIMARY FOCUS. "
                        f"Copy them with 100% accuracy while ensuring perfect fit on the model's body."
                    )
                
                # プロンプトテキストを追加（画像の後）
                prompt_parts.append(prompt_text)
                
                # 進捗報告: API送信
                send_progress = current_progress + int(step_size * 0.3 / num_outputs)
                if self.progress_callback:
                    self.progress_callback(f"Gemini APIに送信中 ({i+1}/{num_outputs})...", send_progress)
                
                # Geminiに画像とプロンプトを送信
                print(f"  Sending request to Gemini 3 Pro Image...")
                response = model.generate_content(prompt_parts)
                
                # 進捗報告: レスポンス処理
                process_progress = current_progress + int(step_size * 0.9 / num_outputs)
                if self.progress_callback:
                    self.progress_callback(f"生成結果を処理中 ({i+1}/{num_outputs})...", process_progress)
                
                # レスポンスから画像を取得
                print(f"  Processing response...")
                if hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                # 画像データを確認
                                if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                                    inline_data = part.inline_data
                                    # バイナリデータからPIL Imageに変換
                                    pil_image = Image.open(BytesIO(inline_data.data))
                                    generated_images.append(pil_image)
                                    print(f"  [OK] Image generated successfully!")
                                    break
                                # テキストレスポンスの場合
                                elif hasattr(part, 'text') and part.text:
                                    print(f"  Text response: {part.text[:100]}...")
            
            metadata = {
                "provider": "google_generative_ai_gemini",
                "model": "gemini-2.5-flash-image",
                "total_images": len(generated_images),
                "requested_images": num_outputs,
                "input_garments": len(garments),
            }
            
            if len(generated_images) == 0:
                print("\n[WARNING] No images were generated. Gemini may have returned text instead.")
            
            return generated_images, metadata
            
        except Exception as e:
            print(f"\n[Google Generative AI] Error: {e}")
            import traceback
            traceback.print_exc()
            # エラーの場合は空リストを返す
            return [], {
                "error": str(e),
                "provider": "google_generative_ai_gemini",
                "model": "gemini-2.5-flash-image"
            }

    def check_api_status(self) -> bool:
        """API接続状態の確認"""
        try:
            # モデル一覧の取得でAPI接続確認
            from google.genai import Client
            client = Client(api_key=self.api_key)
            models = list(client.models.list())
            return len(models) > 0
        except Exception as e:
            print(f"API status check failed: {e}")
            return False

    def estimate_cost(self, config: GenerationConfig) -> float:
        """
        生成コストの見積もり

        Gemini 3 Pro Image Generationの価格:
        - 無料ティア: 一定制限内は無料
        - 有料: 詳細は要確認
        """
        # Geminiモデルは無料ティアがあるため、0として返す
        # 実際の課金については https://ai.google.dev/pricing を参照
        return 0.0

    def supports_seed(self) -> bool:
        """Imagen 4はseedをサポート"""
        return True

    def supports_multi_output(self) -> bool:
        """Imagen 4は複数枚出力をネイティブサポート（1-4枚）"""
        return True

