# Virtual Fashion Try-On - 配布版

## 概要

服の画像をアップロードすると、その服を着たファッションモデルの画像を自動生成するアプリケーションです。

## 配布パッケージの内容

```
VirtualFashionTryOn_v2.0/
├── VirtualFashionTryOn.exe    実行ファイル
├── README.txt                 概要
├── 使い方.txt                  クイックスタート
└── 詳細ガイド.txt              完全ガイド
```

## 配布パッケージのビルド方法

### 1. ビルドスクリプトを実行

```powershell
.\scripts\pack_win.ps1
```

### 2. 自動的に実行される処理

1. 仮想環境の確認と有効化
2. PyInstallerのインストール確認
3. 以前のビルドをクリーニング
4. 実行ファイルのビルド
5. 配布パッケージの作成

### 3. 除外されるファイル

以下のディレクトリとファイルは配布パッケージに含まれません：

#### 除外されるディレクトリ:
- `verification/` - テストプログラム用ディレクトリ
- `tests/` - ユニットテスト
- `venv/` - 仮想環境
- `__pycache__/` - Pythonキャッシュ
- `.git/` - Gitリポジトリ

#### 除外されるファイルタイプ:
- `*.pyc` - コンパイル済みPython
- `*.log` - ログファイル
- `.credentials` - APIキー（セキュリティ）
- `.env` - 環境変数

### 4. 含まれるもの

#### 実行に必要なファイル:
- `VirtualFashionTryOn.exe` - 単一の実行ファイル
- `app/assets/` - アイコンやリソース（埋め込み）

#### ドキュメント:
- `README.txt` - プロジェクト概要
- `使い方.txt` - クイックスタートガイド
- `詳細ガイド.txt` - 完全ガイド

## ビルド設定の詳細

### VirtualFashionTryOn.spec

PyInstallerの.specファイルで以下を設定：

```python
excludes=[
    'verification',      # verificationディレクトリを除外
    'verification.*',    # verificationモジュールを除外
    'tests',            # testsディレクトリを除外
    'tests.*',          # testsモジュールを除外
],
```

### .gitignore

Gitリポジトリから以下を除外：

```
# Verification test outputs (exclude from distribution)
verification/*.png
verification/*.txt
verification/*.jpg
verification/*.jpeg
```

## ビルド後のファイルサイズ

### 予想サイズ:
- **実行ファイル**: 約200-300MB
  - PySide6 (Qt6): 約150MB
  - Python本体: 約30MB
  - 依存ライブラリ: 約50-100MB

### サイズ削減のヒント:

1. **UPX圧縮** (既に有効)
   ```python
   upx=True  # .specファイル内
   ```

2. **不要なモジュールを除外**
   ```python
   excludes=['verification', 'tests', 'pytest']
   ```

3. **onefile形式** (既に有効)
   ```powershell
   --onefile  # 単一ファイルに圧縮
   ```

## 配布前のチェックリスト

### ビルド前:
- [ ] setup_api_key.pyを削除またはAPIキーを削除
- [ ] .credentialsファイルが含まれていないことを確認
- [ ] verificationディレクトリが除外されていることを確認
- [ ] テストコードが除外されていることを確認

### ビルド後:
- [ ] 実行ファイルが正常に起動するか確認
- [ ] APIキー設定ダイアログが表示されるか確認
- [ ] 画像生成が正常に動作するか確認
- [ ] 配布パッケージのファイル一覧を確認

### 配布前:
- [ ] README.txtが含まれているか確認
- [ ] 使い方.txtが含まれているか確認
- [ ] 実行ファイルのファイルサイズを確認
- [ ] ZIPファイルに圧縮

## ビルドエラーのトラブルシューティング

### エラー1: "Module not found"

**原因**: 必要なモジュールがhidden-importに含まれていない

**解決方法**:
```powershell
--hidden-import=モジュール名
```

### エラー2: "Cannot find icon file"

**原因**: アイコンファイルが存在しない

**解決方法**:
1. `app/assets/icons/app_icon.ico`を作成
2. またはビルドスクリプトから`--icon`オプションを削除

### エラー3: "Permission denied"

**原因**: dist/buildフォルダがロックされている

**解決方法**:
```powershell
# フォルダを手動で削除
Remove-Item -Recurse -Force build, dist
```

## 配布方法

### 推奨される配布形式:

1. **ZIP圧縮**
   ```powershell
   Compress-Archive -Path VirtualFashionTryOn_v2.0 -DestinationPath VirtualFashionTryOn_v2.0.zip
   ```

2. **インストーラー作成** (オプション)
   - Inno Setup
   - NSIS
   - WiX Toolset

## ユーザー向け使用方法（配布版）

### 初回起動:

1. `VirtualFashionTryOn.exe`をダブルクリック
2. APIキー自動設定ダイアログで「はい」を選択
3. すぐに使用開始！

### 使い方:

1. 服の画像をアップロード
2. モデル属性を選択
3. 生成開始ボタンをクリック
4. 結果を確認・保存

---

**バージョン**: 2.0.0  
**ビルド日**: 2025年11月11日  
**対応OS**: Windows 10/11

