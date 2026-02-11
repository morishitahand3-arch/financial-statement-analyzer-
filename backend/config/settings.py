"""
アプリケーション設定
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 環境変数を読み込み（プロジェクトルートの.envを明示的に指定）
_env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(_env_path)

# ベースディレクトリ
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Flask設定
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# アップロード設定
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 10485760))  # 10MB
ALLOWED_EXTENSIONS = {"pdf"}

# データディレクトリ
UPLOAD_FOLDER = BASE_DIR / "data" / "uploads"
PROCESSED_FOLDER = BASE_DIR / "data" / "processed"
REPORT_FOLDER = BASE_DIR / "data" / "reports"

# ディレクトリが存在しない場合は作成
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
REPORT_FOLDER.mkdir(parents=True, exist_ok=True)


def allowed_file(filename: str) -> bool:
    """
    アップロードされたファイルが許可された拡張子かチェック

    Args:
        filename: ファイル名

    Returns:
        許可されていればTrue
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
