# Financial Statement Analyzer

企業の決算書（PDF）を分析し、財務指標を計算・解説するWebアプリケーションです。

**バージョン**: 2.0 | **更新日**: 2026年2月7日

## 🎯 目的

- 企業理解度を深める
- 財務諸表の読み方を学ぶ
- 財務分析を自動化・効率化する

## ✨ 主要機能

### 📊 財務分析

- **収益性分析**: ROE、ROA、売上高営業利益率
- **安全性分析**: 自己資本比率、流動比率、固定比率
- **成長性分析**: 前期比成長率（売上高、営業利益、純利益）
- **業績予想比較**: 実績vs予想の達成率評価

### 📈 KPI表示

- 売上高、営業利益、当期純利益を一目で確認
- 前期比較と成長率を自動計算
- 視覚的なグラデーションカードデザイン

### 🤖 AI機能

- **Claude APIによるコメント要約**（オプション）
  - 経営成績のポイント抽出
  - 今後の見通しの要約

### 📊 可視化

- レーダーチャート（財務指標総合）
- 円グラフ（貸借対照表の資産構成）
- 棒グラフ（損益計算書の利益推移）
- タブ切り替えで見やすく整理

## 🛠️ 技術スタック

- **バックエンド**: Python 3.9+
- **Webフレームワーク**: Flask 3.0.0
- **PDF解析**: pdfplumber 0.11.0, PyPDF2 3.0.1
- **AI**: Claude API (Anthropic)
- **フロントエンド**: HTML5, CSS3, JavaScript (ES6+)
- **グラフ**: Chart.js 3.x

## セットアップ

### 前提条件

- Python 3.9以上
- pip

### インストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd financial-statement-analyzer

# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt
```

### 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを編集:

```env
# Flask設定
FLASK_APP=backend/app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Claude API設定（コメント要約機能を使用する場合）
ANTHROPIC_API_KEY=your_api_key_here
```

**注意**: `ANTHROPIC_API_KEY`は任意です。未設定でもコメント要約以外の全機能が動作します。

## 🚀 使い方

### サーバーの起動

```bash
cd backend
python app.py
```

ブラウザで `http://localhost:5000` にアクセスします。

### 基本的な使い方

1. **PDFアップロード**: トップページから決算書PDFを選択
2. **自動分析**: アップロード完了後、自動的に分析が開始されます
3. **結果確認**: 分析結果ページで以下を確認
   - 💰 **主要業績指標（KPI）**: 売上高、営業利益、純利益
   - 📈 **成長性分析**: 前期比成長率と評価コメント
   - 🎯 **業績予想比較**: 達成率の評価（色分け表示）
   - 📊 **収益性・安全性分析**: ROE、ROA、自己資本比率など
   - 💬 **経営陣コメント**: AI要約（APIキー設定時）
   - 📊 **グラフ**: タブ切り替えで各種チャート表示

### スクリーンショット

分析結果画面では、以下の情報が表示されます：

- グラデーションカードで表示されるKPI
- 成長率の色分け表示（緑: 増加、赤: 減少）
- 業績予想の達成率（緑: 90%以上、黄: 80-90%、赤: 80%未満）

## 対応フォーマット

- 有価証券報告書（EDINET形式）
- 決算短信
- その他、標準的な財務諸表のPDF

## 📁 プロジェクト構成

```
financial-statement-analyzer/
├── backend/
│   ├── models/              # データモデル
│   │   ├── balance_sheet.py
│   │   ├── income_statement.py
│   │   ├── forecast.py      # 業績予想（新規）
│   │   ├── cash_flow.py     # キャッシュフロー（新規）
│   │   └── segment.py       # セグメント（新規）
│   ├── services/
│   │   ├── pdf_parser.py          # PDF解析（pdfplumber対応）
│   │   ├── financial_analyzer.py  # 財務分析統合
│   │   └── comment_summarizer.py  # AI要約（新規）
│   ├── analyzers/
│   │   ├── profitability.py       # 収益性分析
│   │   ├── safety.py              # 安全性分析
│   │   ├── growth.py              # 成長性分析（新規）
│   │   ├── forecast_comparison.py # 予想比較（新規）
│   │   └── segment_analyzer.py    # セグメント分析（新規）
│   └── app.py                     # Flaskアプリ
├── frontend/
│   ├── templates/
│   │   └── results.html     # 分析結果画面（大幅拡張）
│   └── static/
│       ├── css/style.css    # スタイル（KPI、成長率など）
│       └── js/
│           ├── charts.js           # 表示ロジック
│           └── financial_charts.js # チャート生成（新規）
├── data/uploads/            # PDFアップロード先
├── IMPLEMENTATION.md        # 詳細実装ドキュメント
└── requirements.txt         # Python依存関係
```

## 開発

### テストの実行

```bash
pytest backend/tests/
```

### コーディング規約

- PEP 8に準拠
- 型ヒントを使用
- Docstringで関数を説明

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 🔮 今後の予定

### Phase 4（次期バージョン）

- [ ] **セグメント分析の完成**
  - セグメント別売上構成比の円グラフ
  - セグメント別営業利益率の棒グラフ
  - 主力セグメントの自動特定

- [ ] **キャッシュフロー分析の充実**
  - CFパターン判定（健全型、成長型、警告型）
  - フリーキャッシュフローの推移グラフ

### 将来の機能

- [ ] 複数期比較機能（3期、5期の推移グラフ）
- [ ] 業界平均との比較
- [ ] EDINET APIとの連携（自動ダウンロード）
- [ ] PDFレポート出力
- [ ] データベース連携（分析履歴の保存）
- [ ] ユーザー認証機能

## 📚 ドキュメント

- **[IMPLEMENTATION.md](IMPLEMENTATION.md)**: 詳細な実装ドキュメント
  - アーキテクチャ説明
  - データフロー
  - PDF解析ロジックの詳細
  - テスト結果
  - トラブルシューティング

- **[CLAUDE.md](CLAUDE.md)**: Claude Code用のコンテキスト情報

## 🐛 トラブルシューティング

### 数値が正しく表示されない

- ブラウザのキャッシュをクリア: **Ctrl + Shift + R**
- Flaskアプリを再起動

### PDF解析がうまくいかない

- デバッグスクリプトで確認:
  ```bash
  python test_pdf_extraction.py
  ```
- 対応フォーマット: 日本企業の決算短信・有価証券報告書

### Claude APIエラー

- `.env`ファイルで`ANTHROPIC_API_KEY`が正しく設定されているか確認
- APIキーなしでもコメント要約以外は動作します
