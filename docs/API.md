# API ドキュメント

## エンドポイント一覧

### 1. ファイルアップロード

**エンドポイント**: `POST /api/upload`

**説明**: PDFファイルをアップロードして処理を開始します。

**リクエスト**:
- Content-Type: `multipart/form-data`
- Body:
  - `file`: PDFファイル（最大10MB）

**レスポンス** (200 OK):
```json
{
  "message": "ファイルが正常にアップロードされました",
  "filename": "financial_statement.pdf",
  "status": "processing"
}
```

**エラーレスポンス** (400 Bad Request):
```json
{
  "error": "ファイルが選択されていません"
}
```

### 2. 分析結果取得

**エンドポイント**: `GET /api/analyze/<filename>`

**説明**: アップロードされたファイルの分析結果を取得します。

**パラメータ**:
- `filename`: ファイル名

**レスポンス** (200 OK):
```json
{
  "filename": "financial_statement.pdf",
  "status": "completed",
  "results": {
    "profitability": {
      "roe": 12.5,
      "roa": 8.3,
      "operating_margin": 15.2,
      "comments": ["...", "..."],
      "description": {...}
    },
    "safety": {
      "equity_ratio": 45.6,
      "current_ratio": 180.3,
      "fixed_ratio": 95.2,
      "comments": ["...", "..."],
      "description": {...}
    },
    "growth": {},
    "efficiency": {}
  }
}
```

## ステータスコード

- `200 OK`: 成功
- `400 Bad Request`: リクエストが不正
- `404 Not Found`: リソースが見つからない
- `413 Payload Too Large`: ファイルサイズが大きすぎる
- `500 Internal Server Error`: サーバーエラー

## エラーハンドリング

全てのエラーレスポンスは以下の形式で返されます:

```json
{
  "error": "エラーメッセージ"
}
```

## 使用例

### cURL

```bash
# ファイルアップロード
curl -X POST http://localhost:5000/api/upload \
  -F "file=@financial_statement.pdf"

# 分析結果取得
curl http://localhost:5000/api/analyze/financial_statement.pdf
```

### JavaScript (Fetch API)

```javascript
// ファイルアップロード
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('/api/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();

// 分析結果取得
const analysisResponse = await fetch(`/api/analyze/${data.filename}`);
const analysisData = await analysisResponse.json();
```
