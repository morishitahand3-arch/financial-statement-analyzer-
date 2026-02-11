"""
財務分析サービス
"""
from typing import Dict, Optional, List
from models.balance_sheet import BalanceSheet
from models.income_statement import IncomeStatement
from models.forecast import PerformanceForecast
from models.cash_flow import CashFlowStatement
from models.segment import SegmentAnalysis, Segment
from analyzers.profitability import analyze_profitability
from analyzers.safety import analyze_safety
from analyzers.growth import analyze_growth
from analyzers.forecast_comparison import analyze_forecast_comparison
from analyzers.segment_analyzer import analyze_segments
from services.comment_summarizer import summarize_company_comments


class FinancialAnalyzer:
    """財務分析クラス"""

    def __init__(
        self, balance_sheet: BalanceSheet, income_statement: IncomeStatement
    ):
        """
        Args:
            balance_sheet: 貸借対照表
            income_statement: 損益計算書
        """
        self.balance_sheet = balance_sheet
        self.income_statement = income_statement

    def analyze(self) -> Dict[str, any]:
        """
        全ての財務分析を実行

        Returns:
            分析結果の辞書
        """
        return {
            "profitability": analyze_profitability(
                self.income_statement, self.balance_sheet
            ),
            "safety": analyze_safety(self.balance_sheet),
            # TODO: 成長性分析と効率性分析を追加
            # "growth": analyze_growth(...),
            # "efficiency": analyze_efficiency(...),
            "company_info": {
                "name": self.balance_sheet.company_name,
                "fiscal_year": self.balance_sheet.fiscal_year,
            },
        }


def analyze_financial_statements(
    balance_sheet_data: Dict,
    income_statement_data: Dict,
    previous_income_statement_data: Optional[Dict] = None,
    forecast_data: Optional[Dict] = None,
    cash_flow_data: Optional[Dict] = None,
    segment_data: Optional[List[Dict]] = None,
    company_comments: Optional[Dict[str, str]] = None,
    amount_unit: str = "thousand"
) -> Dict[str, any]:
    """
    財務諸表データから分析を実行

    Args:
        balance_sheet_data: 貸借対照表データ
        income_statement_data: 損益計算書データ
        previous_income_statement_data: 前期の損益計算書データ（オプション）
        forecast_data: 業績予想データ（オプション）
        cash_flow_data: キャッシュフローデータ（オプション）
        segment_data: セグメントデータ（オプション）
        company_comments: 会社コメントデータ（オプション）
        amount_unit: 金額単位 "million"（百万円）or "thousand"（千円）

    Returns:
        分析結果
    """
    # 百万円単位の場合は変換不要、千円単位の場合は÷1000で百万円に変換
    divisor = 1000 if amount_unit == "thousand" else 1
    # データモデルに変換
    balance_sheet = BalanceSheet(
        total_assets=balance_sheet_data.get('total_assets', 0.0),
        current_assets=balance_sheet_data.get('current_assets', 0.0),
        fixed_assets=balance_sheet_data.get('fixed_assets', 0.0),
        total_liabilities=balance_sheet_data.get('total_liabilities', 0.0),
        total_net_assets=balance_sheet_data.get('total_net_assets', 0.0),
        shareholders_equity=balance_sheet_data.get('shareholders_equity', 0.0),
        current_liabilities=balance_sheet_data.get('current_liabilities', 0.0),
        company_name=balance_sheet_data.get('company_name'),
        fiscal_year=balance_sheet_data.get('fiscal_year'),
    )
    income_statement = IncomeStatement(
        revenue=income_statement_data.get('revenue', 0.0),
        operating_income=income_statement_data.get('operating_income', 0.0),
        net_income=income_statement_data.get('net_income', 0.0),
        company_name=income_statement_data.get('company_name'),
        fiscal_year=income_statement_data.get('fiscal_year'),
    )

    # 基本分析を実行
    analyzer = FinancialAnalyzer(balance_sheet, income_statement)
    results = analyzer.analyze()

    # 貸借対照表の金額データを百万円単位に変換
    if "safety" in results:
        safety = results["safety"]
        # 金額データのみを変換（比率データは変換しない）
        amount_keys = ["current_assets", "fixed_assets", "total_assets",
                      "current_liabilities", "fixed_liabilities", "total_net_assets", "total_liabilities"]
        for key in amount_keys:
            if key in safety and safety[key] is not None:
                safety[key] = safety[key] / divisor

    # 前期データがあれば成長性分析を追加
    if previous_income_statement_data:
        previous_is = IncomeStatement(
            revenue=previous_income_statement_data.get('revenue', 0.0),
            operating_income=previous_income_statement_data.get('operating_income', 0.0),
            net_income=previous_income_statement_data.get('net_income', 0.0),
        )
        results["growth"] = analyze_growth(income_statement, previous_is)
    else:
        results["growth"] = {"has_comparison": False}

    # 業績予想データがあれば予想比較分析を追加
    if forecast_data:
        forecast = PerformanceForecast.from_dict(forecast_data)
        results["forecast_comparison"] = analyze_forecast_comparison(income_statement, forecast)

        # 業績予想の金額データを百万円単位に変換
        if results["forecast_comparison"].get("has_forecast"):
            fc = results["forecast_comparison"]
            for metric in ["revenue", "operating_income", "net_income"]:
                if metric in fc and fc[metric]:
                    if "actual" in fc[metric] and fc[metric]["actual"] is not None:
                        fc[metric]["actual"] = fc[metric]["actual"] / divisor
                    if "forecast" in fc[metric] and fc[metric]["forecast"] is not None:
                        fc[metric]["forecast"] = fc[metric]["forecast"] / divisor

            # 修正履歴の金額データも変換
            if "revisions" in fc and fc["revisions"]:
                for revision in fc["revisions"]:
                    amount_keys = ["previous_revenue", "revised_revenue",
                                 "previous_operating_income", "revised_operating_income",
                                 "previous_net_income", "revised_net_income"]
                    for key in amount_keys:
                        if key in revision and revision[key] is not None:
                            revision[key] = revision[key] / divisor
    else:
        results["forecast_comparison"] = {"has_forecast": False}

    # キャッシュフローデータを追加
    if cash_flow_data:
        cash_flow = CashFlowStatement.from_dict(cash_flow_data)
        results["cash_flow"] = {
            "data": cash_flow.to_dict(),
            "type": cash_flow.get_cash_flow_type()
        }
    else:
        results["cash_flow"] = None

    # セグメントデータを追加
    if segment_data:
        segments = [Segment.from_dict(seg) for seg in segment_data]
        total_revenue = sum(seg.revenue for seg in segments)
        segment_analysis_obj = SegmentAnalysis(
            segments=segments,
            total_revenue=total_revenue
        )
        results["segment_analysis"] = analyze_segments(segment_analysis_obj)
    else:
        results["segment_analysis"] = {"has_segments": False}

    # 会社コメントの要約を追加
    if company_comments:
        results["company_comments"] = summarize_company_comments(company_comments)
    else:
        results["company_comments"] = {"has_summaries": False}

    # 主要業績指標（KPI）を整形（百万円単位に変換）
    results["key_metrics"] = {
        "revenue": {
            "current": income_statement.revenue / divisor if income_statement.revenue else 0,
            "previous": previous_income_statement_data.get('revenue') / divisor if previous_income_statement_data and previous_income_statement_data.get('revenue') else None,
            "growth_rate": results.get("growth", {}).get("revenue_growth")
        },
        "operating_income": {
            "current": income_statement.operating_income / divisor if income_statement.operating_income else 0,
            "previous": previous_income_statement_data.get('operating_income') / divisor if previous_income_statement_data and previous_income_statement_data.get('operating_income') else None,
            "growth_rate": results.get("growth", {}).get("operating_income_growth")
        },
        "net_income": {
            "current": income_statement.net_income / divisor if income_statement.net_income else 0,
            "previous": previous_income_statement_data.get('net_income') / divisor if previous_income_statement_data and previous_income_statement_data.get('net_income') else None,
            "growth_rate": results.get("growth", {}).get("net_income_growth")
        }
    }

    return results
