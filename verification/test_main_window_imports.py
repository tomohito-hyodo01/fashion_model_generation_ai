"""Main window import test"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Main Window インポートテスト")
print("=" * 70)

try:
    # メインウィンドウをインポート
    from app.ui.main_window import (
        MainWindow,
        GenerationWorker,
        ChatRefinementWorker,
        VideoGenerationWorker,
        FashnTryonWorker
    )
    
    print("[OK] MainWindow")
    print("[OK] GenerationWorker")
    print("[OK] ChatRefinementWorker")
    print("[OK] VideoGenerationWorker")
    print("[OK] FashnTryonWorker")
    
    print("\n[SUCCESS] すべてのクラスをインポートできました")
    
    # メソッドの存在確認
    print("\n" + "=" * 70)
    print("メソッド存在確認")
    print("=" * 70)
    
    methods_to_check = [
        "_setup_ui",
        "_create_upload_group",
        "_create_reference_person_group",
        "_create_model_attributes_group",
        "_create_generation_settings_group",
        "_create_gallery_group",
        "_create_history_group",
        "_create_chat_group",
        "_create_video_group",
        "_start_generation",
        "_on_generation_completed",
        "_on_generation_failed",
    ]
    
    for method_name in methods_to_check:
        if hasattr(MainWindow, method_name):
            print(f"[OK] {method_name}")
        else:
            print(f"[MISSING] {method_name}")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] エラーチェック完了")
    print("=" * 70)
    
except Exception as e:
    print(f"\n[ERROR] インポートエラー: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

