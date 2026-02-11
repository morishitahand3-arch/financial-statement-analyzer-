"""
貸借対照表（Balance Sheet）のデータモデル
"""
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class BalanceSheet:
    """貸借対照表"""

    # 資産の部
    current_assets: float = 0.0
    cash_and_deposits: Optional[float] = None
    accounts_receivable: Optional[float] = None
    inventory: Optional[float] = None

    fixed_assets: float = 0.0
    tangible_assets: Optional[float] = None
    intangible_assets: Optional[float] = None
    investments: Optional[float] = None

    total_assets: float = 0.0

    # 負債の部
    current_liabilities: float = 0.0
    accounts_payable: Optional[float] = None
    short_term_debt: Optional[float] = None

    long_term_liabilities: float = 0.0
    long_term_debt: Optional[float] = None

    total_liabilities: float = 0.0

    # 純資産の部
    shareholders_equity: float = 0.0
    capital_stock: Optional[float] = None
    retained_earnings: Optional[float] = None

    total_net_assets: float = 0.0

    # メタデータ
    fiscal_year: Optional[str] = None
    company_name: Optional[str] = None
