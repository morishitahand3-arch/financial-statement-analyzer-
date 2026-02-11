"""
収益性分析（Profitability Analysis）
"""
from typing import Dict, Optional
from models.balance_sheet import BalanceSheet
from models.income_statement import IncomeStatement


def calculate_roe(
    income_statement: IncomeStatement, balance_sheet: BalanceSheet
) -> Optional[float]:
    """
    ROE（自己資本利益率）を計算

    ROE = 当期純利益 ÷ 自己資本 × 100

    Args:
        income_statement: 損益計算書
        balance_sheet: 貸借対照表

    Returns:
        ROE（%）、計算できない場合はNone
    """
    if balance_sheet.shareholders_equity == 0:
        return None

    return (income_statement.net_income / balance_sheet.shareholders_equity) * 100


def calculate_roa(
    income_statement: IncomeStatement, balance_sheet: BalanceSheet
) -> Optional[float]:
    """
    ROA（総資産利益率）を計算

    ROA = 当期純利益 ÷ 総資産 × 100

    Args:
        income_statement: 損益計算書
        balance_sheet: 貸借対照表

    Returns:
        ROA（%）、計算できない場合はNone
    """
    if balance_sheet.total_assets == 0:
        return None

    return (income_statement.net_income / balance_sheet.total_assets) * 100


def calculate_operating_margin(income_statement: IncomeStatement) -> Optional[float]:
    """
    売上高営業利益率を計算

    売上高営業利益率 = 営業利益 ÷ 売上高 × 100

    Args:
        income_statement: 損益計算書

    Returns:
        売上高営業利益率（%）、計算できない場合はNone
    """
    if income_statement.revenue == 0:
        return None

    return (income_statement.operating_income / income_statement.revenue) * 100


def analyze_profitability(
    income_statement: IncomeStatement, balance_sheet: BalanceSheet
) -> Dict[str, any]:
    """
    収益性分析を実行

    Args:
        income_statement: 損益計算書
        balance_sheet: 貸借対照表

    Returns:
        分析結果の辞書
    """
    roe = calculate_roe(income_statement, balance_sheet)
    roa = calculate_roa(income_statement, balance_sheet)
    operating_margin = calculate_operating_margin(income_statement)

    # 評価コメント
    comments = []
    if roe is not None:
        if roe >= 10:
            comments.append("ROEが10%以上で、株主資本を効率的に活用しています。")
        elif roe >= 5:
            comments.append("ROEは平均的な水準です。")
        else:
            comments.append("ROEが低く、収益性の改善が必要です。")

    if operating_margin is not None:
        if operating_margin >= 10:
            comments.append("営業利益率が高く、本業で高い収益力があります。")
        elif operating_margin >= 5:
            comments.append("営業利益率は標準的な水準です。")
        else:
            comments.append("営業利益率が低く、コスト管理の改善が求められます。")

    return {
        "roe": round(roe, 2) if roe is not None else None,
        "roa": round(roa, 2) if roa is not None else None,
        "operating_margin": round(operating_margin, 2)
        if operating_margin is not None
        else None,
        "comments": comments,
        "description": {
            "roe": "自己資本利益率。株主資本をどれだけ効率的に使って利益を出しているかを示す指標。",
            "roa": "総資産利益率。会社の資産全体をどれだけ効率的に運用しているかを示す指標。",
            "operating_margin": "売上高営業利益率。本業でどれだけ効率的に利益を出しているかを示す指標。",
        },
    }
