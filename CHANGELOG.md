# Changelog

## [1.1.0] - 2024-11-04

### Added
- ⭐ **Stability AI SD 3.5対応**: image-to-image機能で衣類画像を直接参照
- 画像参照機能により衣類の忠実再現が大幅に向上
- SD 3.5の最新APIエンドポイント対応（v2beta）
- image-to-imageモードとtext-to-imageモードの自動切り替え

### Changed
- デフォルトプロバイダをStability AI SD 3.5に変更
- プロンプト生成ロジックを改善（よりシンプルで効果的に）
- 情報ダイアログを更新（画像参照機能の説明を追加）
- UIの表示名を「Stability AI SD 3.5 ⭐推奨：画像参照」に更新

### Improved
- 衣類画像の忠実度が大幅に向上（テキストのみ vs 画像参照）
- 日本語ファイル名の画像読み込みに完全対応
- 全身写真生成の精度向上

### Fixed
- OpenAIコンテンツフィルター対策（プロンプトを最適化）
- 日本語パスのエンコーディングエラーを修正
- Qt 6の非推奨警告を解消

## [1.0.0] - 2024-11-04

### Initial Release
- 基本的な画像生成機能
- OpenAI (DALL-E 3)、Stability AI、Google Imagen対応
- PySide6 GUI
- APIキー暗号化（DPAPI/Fernet）
- 忠実度検証機能
- 1-4枚の画像生成




