"""
キャッシュフロー計算書データモデル

企業の資金の流れを示すキャッシュフロー計算書のデータを格納する。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CashFlowStatement:
    """
    キャッシュフロー計算書

    Attributes:
        operating_cash_flow: 営業活動によるキャッシュフロー（百万円）
        investing_cash_flow: 投資活動によるキャッシュフロー（百万円）
        financing_cash_flow: 財務活動によるキャッシュフロー（百万円）
        free_cash_flow: フリーキャッシュフロー（営業CF + 投資CF）（百万円）
        fiscal_year: 対象会計年度（例: "2024年3月期"）
        company_name: 会社名
    """
    operating_cash_flow: float = 0.0
    investing_cash_flow: float = 0.0
    financing_cash_flow: float = 0.0
    free_cash_flow: Optional[float] = None
    fiscal_year: Optional[str] = None
    company_name: Optional[str] = None

    def __post_init__(self):
        """フリーキャッシュフローを自動計算"""
        if self.free_cash_flow is None:
            self.free_cash_flow = self.operating_cash_flow + self.investing_cash_flow

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "operating_cash_flow": self.operating_cash_flow,
            "investing_cash_flow": self.investing_cash_flow,
            "financing_cash_flow": self.financing_cash_flow,
            "free_cash_flow": self.free_cash_flow,
            "fiscal_year": self.fiscal_year,
            "company_name": self.company_name
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CashFlowStatement":
        """辞書から生成"""
        return cls(
            operating_cash_flow=data.get("operating_cash_flow", 0.0),
            investing_cash_flow=data.get("investing_cash_flow", 0.0),
            financing_cash_flow=data.get("financing_cash_flow", 0.0),
            free_cash_flow=data.get("free_cash_flow"),
            fiscal_year=data.get("fiscal_year"),
            company_name=data.get("company_name")
        )

    def get_cash_flow_type(self) -> str:
        """
        キャッシュフロー型を判定

        Returns:
            "healthy": 営業CF+、投資CF-、財務CF- (理想的)
            "growing": 営業CF+、投資CF-、財務CF+ (成長期)
            "warning": 営業CF-
            "other": その他
        """
        if self.operating_cash_flow > 0:
            if self.investing_cash_flow < 0 and self.financing_cash_flow < 0:
                return "healthy"
            elif self.investing_cash_flow < 0 and self.financing_cash_flow > 0:
                return "growing"
            else:
                return "other"
        else:
            return "warning"
