# Contributing to Virtual Fashion Try-On

このプロジェクトへの貢献を歓迎します！

## 開発環境のセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/yourname/virtual-fashion-tryon.git
cd virtual-fashion-tryon

# 仮想環境を作成
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 依存パッケージをインストール
pip install -r requirements.txt
pip install -e ".[dev]"

# テストを実行
pytest
```

## コーディング規約

- PEP 8に準拠
- 最大行長: 100文字
- 型ヒントを使用
- docstringを記載（Google Style）

### フォーマット

```bash
# コードフォーマット
black .

# リンター
ruff check .
```

## テスト

新機能を追加する場合は、必ずテストを追加してください。

```bash
# 全テストを実行
pytest

# カバレッジレポート
pytest --cov=app --cov-report=html
```

## プルリクエスト

1. フォークしてブランチを作成
2. 変更を加える
3. テストを追加・実行
4. プルリクエストを作成

### プルリクエストの要件

- [ ] テストが全て通る
- [ ] コードがフォーマットされている
- [ ] docstringが記載されている
- [ ] 変更内容が説明されている

## ライセンス

貢献されたコードはMITライセンスの下で公開されます。



