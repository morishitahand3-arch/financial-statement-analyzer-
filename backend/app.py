"""
Financial Statement Analyzer - メインアプリケーション
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pathlib import Path

from config.settings import (
    SECRET_KEY,
    DEBUG,
    UPLOAD_FOLDER,
    ALLOWED_EXTENSIONS,
    allowed_file,
)

# Flaskアプリケーションの初期化
app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static",
)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB

# CORSを有効化
CORS(app)


@app.route("/")
def index():
    """トップページ"""
    return render_template("index.html")


@app.route("/upload")
def upload_page():
    """アップロードページ"""
    return render_template("upload.html")


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """
    PDFファイルをアップロード

    Returns:
        JSONレスポンス
    """
    if "file" not in request.files:
        return jsonify({"error": "ファイルが選択されていません"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "ファイルが選択されていません"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "PDFファイルのみアップロード可能です"}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # TODO: ここでPDF解析と財務分析を実行
        # from services.pdf_parser import parse_pdf
        # from services.financial_analyzer import analyze
        # result = analyze(parse_pdf(filepath))

        return jsonify({
            "message": "ファイルが正常にアップロードされました",
            "filename": filename,
            "status": "processing",
        }), 200


@app.route("/api/analyze/<filename>", methods=["GET"])
def analyze_file(filename):
    """
    アップロードされたファイルを分析

    Args:
        filename: ファイル名

    Returns:
        分析結果のJSON
    """
    from services.pdf_parser import parse_pdf
    from services.financial_analyzer import analyze_financial_statements

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "ファイルが見つかりません"}), 404

    try:
        # PDFから財務データを抽出
        financial_data = parse_pdf(filepath)

        # fiscal_year情報をincome_statementとforecastに追加
        fiscal_year = financial_data.get("fiscal_year")
        if fiscal_year:
            if financial_data.get("income_statement"):
                financial_data["income_statement"]["fiscal_year"] = fiscal_year
            if financial_data.get("forecast"):
                financial_data["forecast"]["fiscal_year"] = fiscal_year

        # 財務分析を実行
        if financial_data.get("balance_sheet") and financial_data.get("income_statement"):
            analysis_results = analyze_financial_statements(
                balance_sheet_data=financial_data["balance_sheet"],
                income_statement_data=financial_data["income_statement"],
                previous_income_statement_data=financial_data.get("previous_income_statement"),
                forecast_data=financial_data.get("forecast"),
                cash_flow_data=financial_data.get("cash_flow"),
                segment_data=financial_data.get("segments"),
                company_comments=financial_data.get("company_comments"),
                amount_unit=financial_data.get("amount_unit", "thousand")
            )

            return jsonify({
                "filename": filename,
                "status": "completed",
                "company_name": financial_data.get("company_name", "不明"),
                "fiscal_year": financial_data.get("fiscal_year", "不明"),
                "results": analysis_results,
            })
        else:
            return jsonify({
                "error": "財務データを抽出できませんでした",
                "message": "PDFから貸借対照表または損益計算書のデータが見つかりませんでした。"
            }), 400

    except Exception as e:
        import traceback
        # エラーの詳細をログに出力
        print(f"Error analyzing {filename}: {str(e)}")
        print(traceback.format_exc())

        # エラーの種類に応じたメッセージを返す
        error_message = str(e)
        if "DependencyError" in str(type(e)) or "PyCryptodome" in str(e):
            error_message = "暗号化されたPDFを読み込むために必要なライブラリ(PyCryptodome)がインストールされていません。"
        elif "FileNotFoundError" in str(type(e)):
            error_message = "PDFファイルが見つかりません。"
        elif "PDF解析エラー" in str(e):
            error_message = f"PDFの解析に失敗しました: {str(e)}"

        return jsonify({
            "error": "分析中にエラーが発生しました",
            "message": error_message,
            "details": str(e) if DEBUG else None
        }), 500


@app.route("/results")
def results_page():
    """分析結果ページ"""
    return render_template("results.html")


@app.route("/test")
def test_page():
    """テストページ"""
    return render_template("test.html")


@app.errorhandler(413)
def request_entity_too_large(error):
    """ファイルサイズ超過エラー"""
    return jsonify({"error": "ファイルサイズが大きすぎます（最大10MB）"}), 413


@app.errorhandler(404)
def not_found(error):
    """404エラー"""
    return jsonify({"error": "ページが見つかりません"}), 404


@app.errorhandler(500)
def internal_error(error):
    """500エラー"""
    return jsonify({"error": "サーバーエラーが発生しました"}), 500


if __name__ == "__main__":
    print(f"Starting Financial Statement Analyzer...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Debug mode: {DEBUG}")
    # use_reloader=False: auto-reloadを無効化（頻繁な再起動を防ぐ）
    app.run(debug=DEBUG, host="0.0.0.0", port=5000, use_reloader=False)
