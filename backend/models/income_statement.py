"""
損益計算書（Income Statement）のデータモデル
"""
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class IncomeStatement:
    """損益計算書"""

    # 売上
    revenue: float = 0.0
    cost_of_sales: float = 0.0

    # 利益
    gross_profit: Optional[float] = None
    operating_income: float = 0.0
    ordinary_income: Optional[float] = None
    net_income: float = 0.0

    # 費用
    selling_general_admin: Optional[float] = None
    depreciation: Optional[float] = None

    # 営業外損益
    non_operating_income: Optional[float] = None
    non_operating_expenses: Optional[float] = None

    # メタデータ
    fiscal_year: Optional[str] = None
    company_name: Optional[str] = None
