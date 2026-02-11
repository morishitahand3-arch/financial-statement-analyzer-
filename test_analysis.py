"""直接APIをテストするスクリプト"""
import sys
sys.path.insert(0, 'backend')

from services.pdf_parser import parse_pdf
from services.financial_analyzer import analyze_financial_statements

# アップロードされたファイルをテスト
filepath = "data/uploads/260203.pdf"

try:
    print("PDFを解析中...")
    financial_data = parse_pdf(filepath)

    print("[OK] PDF解析成功")
    print(f"  会社名: {financial_data.get('company_name', '不明')}")
    print(f"  会計年度: {financial_data.get('fiscal_year', '不明')}")
    print(f"  貸借対照表: {'あり' if financial_data.get('balance_sheet') else 'なし'}")
    print(f"  損益計算書: {'あり' if financial_data.get('income_statement') else 'なし'}")

    if financial_data.get('balance_sheet') and financial_data.get('income_statement'):
        print("\n財務分析を実行中...")
        results = analyze_financial_statements(
            balance_sheet_data=financial_data['balance_sheet'],
            income_statement_data=financial_data['income_statement']
        )
        print("[OK] 財務分析成功")
        print(f"  ROE: {results.get('profitability', {}).get('roe')}%")
        print(f"  自己資本比率: {results.get('safety', {}).get('equity_ratio')}%")
    else:
        print("[ERROR] 財務データが不完全です")

except Exception as e:
    print(f"[ERROR] エラー: {e}")
    import traceback
    traceback.print_exc()
