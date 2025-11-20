"""Information dialog for user guidance"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextBrowser
from PySide6.QtCore import Qt


class InfoDialog(QDialog):
    """情報ダイアログ"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("重要な情報")
        self.setMinimumWidth(600)
        self._setup_ui()

    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout(self)

        # 情報テキスト
        info_text = QTextBrowser()
        info_text.setHtml("""
        <h2>衣類画像の忠実な再現について</h2>
        
        <h3>画像参照機能について</h3>
        <p><b>Stability AI SD 3.5</b>を使用すると、衣類画像を<b>直接参照</b>して
        モデルに着せた画像を生成できます。これにより忠実度が大幅に向上します！</p>
        
        <h3>推奨設定（最良の結果のため）</h3>
        <ul>
            <li><b>Stability AI SD 3.5</b>を選択（画像参照機能）</li>
            <li>高品質な衣類画像を使用（512x512以上、背景が白）</li>
            <li>高品質（HD）を選択</li>
            <li>複数枚（2-4枚）生成して最良を選択</li>
        </ul>
        
        <h3>制限事項</h3>
        <p><b>DALL-E 3（OpenAI）</b>と<b>Google Imagen</b>は、テキストプロンプトのみで
        画像参照機能がないため、衣類の完全な再現は困難です。</p>
        
        <h3>Stability AI SD 3.5の動作</h3>
        <p><b>image-to-image機能</b>を使用：</p>
        <ol>
            <li>衣類画像を<b>参照画像</b>としてAPIに送信</li>
            <li>AIが参照画像の衣類を認識</li>
            <li>その衣類を着たモデル画像を生成</li>
        </ol>
        
        <p><b>メリット：</b>テキスト記述よりも遥かに正確に衣類を再現できます！</p>
        
        <h3>他のAI（OpenAI/Imagen）の動作</h3>
        <ol>
            <li>衣類画像の色・パターンを自動分析</li>
            <li>分析結果をテキスト記述に変換</li>
            <li>テキストプロンプトとしてAIに送信</li>
        </ol>
        
        <p><b>注意：</b>画像参照がないため、類似の衣類が生成されますが
        完全な複製は困難です。</p>
        
        <h3>最良の結果を得るために</h3>
        <ul>
            <li>衣類画像は高解像度、背景が白または透過のものを使用</li>
            <li>シンプルなデザインの衣類の方が再現性が高い</li>
            <li>生成後、結果を確認して再生成を試みる</li>
        </ul>
        """)
        info_text.setOpenExternalLinks(True)
        layout.addWidget(info_text)

        # 閉じるボタン
        close_btn = QPushButton("理解しました")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

