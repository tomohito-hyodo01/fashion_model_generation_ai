"""
All imports test - すべてのモジュールが正しくインポートできるか確認
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_phase1_imports():
    """Phase 1のインポートテスト"""
    print("\n" + "=" * 70)
    print("Phase 1 インポートテスト")
    print("=" * 70)
    
    try:
        from app.ui.widgets.pose_gallery import PoseGalleryWidget
        print("[OK] PoseGalleryWidget")
        
        from app.ui.widgets.background_gallery import BackgroundGalleryWidget
        print("[OK] BackgroundGalleryWidget")
        
        from app.core.vton.pose_extractor import PoseExtractor
        print("[OK] PoseExtractor")
        
        print("\n[SUCCESS] Phase 1 すべてのモジュールをインポートできました")
        return True
    except Exception as e:
        print(f"\n[ERROR] Phase 1 インポートエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase2_imports():
    """Phase 2のインポートテスト"""
    print("\n" + "=" * 70)
    print("Phase 2 インポートテスト")
    print("=" * 70)
    
    try:
        from app.core.pipeline.multi_angle_generator import MultiAngleGenerator
        print("[OK] MultiAngleGenerator")
        
        from app.ui.widgets.chat_refinement import ChatRefinementWidget
        print("[OK] ChatRefinementWidget")
        
        from app.core.pipeline.chat_instruction_parser import ChatInstructionParser
        print("[OK] ChatInstructionParser")
        
        from app.core.pipeline.chat_refinement_service import ChatRefinementService
        print("[OK] ChatRefinementService")
        
        print("\n[SUCCESS] Phase 2 すべてのモジュールをインポートできました")
        return True
    except Exception as e:
        print(f"\n[ERROR] Phase 2 インポートエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase3_imports():
    """Phase 3のインポートテスト"""
    print("\n" + "=" * 70)
    print("Phase 3 インポートテスト")
    print("=" * 70)
    
    try:
        from app.core.history.history_manager import HistoryManager
        print("[OK] HistoryManager")
        
        from app.core.history.project_manager import ProjectManager
        print("[OK] ProjectManager")
        
        from app.ui.widgets.history_panel import HistoryPanel
        print("[OK] HistoryPanel")
        
        from app.core.vton.color_changer import ColorChanger
        print("[OK] ColorChanger")
        
        from app.core.pipeline.batch_processor import BatchProcessor
        print("[OK] BatchProcessor")
        
        from app.utils.settings_manager import SettingsManager
        print("[OK] SettingsManager")
        
        print("\n[SUCCESS] Phase 3 すべてのモジュールをインポートできました")
        return True
    except Exception as e:
        print(f"\n[ERROR] Phase 3 インポートエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_window():
    """メインウィンドウのインポートテスト"""
    print("\n" + "=" * 70)
    print("メインウィンドウ インポートテスト")
    print("=" * 70)
    
    try:
        from app.ui.main_window import MainWindow, GenerationWorker, ChatRefinementWorker
        print("[OK] MainWindow")
        print("[OK] GenerationWorker")
        print("[OK] ChatRefinementWorker")
        
        print("\n[SUCCESS] メインウィンドウのすべてのクラスをインポートできました")
        return True
    except Exception as e:
        print(f"\n[ERROR] メインウィンドウ インポートエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """依存パッケージの確認"""
    print("\n" + "=" * 70)
    print("依存パッケージ確認")
    print("=" * 70)
    
    required_packages = {
        "PySide6": "PySide6",
        "PIL": "Pillow",
        "cv2": "opencv-python",
        "numpy": "numpy",
        "requests": "requests",
        "google.generativeai": "google-generativeai",
    }
    
    all_ok = True
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"[OK] {package_name}")
        except ImportError:
            print(f"[MISSING] {package_name} - pip install {package_name}")
            all_ok = False
    
    # オプショナルパッケージ
    optional_packages = {
        "mediapipe": "mediapipe"
    }
    
    print("\nオプショナルパッケージ:")
    for module_name, package_name in optional_packages.items():
        try:
            __import__(module_name)
            print(f"[OK] {package_name}")
        except ImportError:
            print(f"[OPTIONAL] {package_name} - pip install {package_name}")
    
    if all_ok:
        print("\n[SUCCESS] すべての必須パッケージがインストールされています")
    else:
        print("\n[WARNING] いくつかのパッケージが不足しています")
    
    return all_ok

def main():
    """すべてのテストを実行"""
    print("=" * 70)
    print("Virtual Fashion Try-On v2.0 - 総合インポートテスト")
    print("=" * 70)
    
    results = []
    
    # 依存パッケージ確認
    results.append(("依存パッケージ", test_dependencies()))
    
    # Phase 1テスト
    results.append(("Phase 1", test_phase1_imports()))
    
    # Phase 2テスト
    results.append(("Phase 2", test_phase2_imports()))
    
    # Phase 3テスト
    results.append(("Phase 3", test_phase3_imports()))
    
    # メインウィンドウテスト
    results.append(("メインウィンドウ", test_main_window()))
    
    # 結果サマリー
    print("\n" + "=" * 70)
    print("テスト結果サマリー")
    print("=" * 70)
    
    all_passed = True
    for name, result in results:
        status = "[OK]" if result else "[FAILED]"
        print(f"{status} {name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("[SUCCESS] すべてのテストに合格しました！")
        print("アプリケーションは正常に動作する準備が整っています。")
    else:
        print("[WARNING] いくつかのテストが失敗しました。")
        print("エラーメッセージを確認してください。")
    print("=" * 70)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


