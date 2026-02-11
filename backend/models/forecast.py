"""
業績予想データモデル

企業の業績予想情報を格納するデータクラス。
実績との比較分析に使用される。
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class ForecastRevision:
    """
    業績予想の修正履歴

    Attributes:
        revision_date: 修正日（例: "2025年11月1日"）
        previous_revenue: 修正前の売上高予想（百万円）
        revised_revenue: 修正後の売上高予想（百万円）
        previous_operating_income: 修正前の営業利益予想（百万円）
        revised_operating_income: 修正後の営業利益予想（百万円）
        previous_net_income: 修正前の当期純利益予想（百万円）
        revised_net_income: 修正後の当期純利益予想（百万円）
        reason: 修正理由
    """
    revision_date: Optional[str] = None
    previous_revenue: Optional[float] = None
    revised_revenue: Optional[float] = None
    previous_operating_income: Optional[float] = None
    revised_operating_income: Optional[float] = None
    previous_net_income: Optional[float] = None
    revised_net_income: Optional[float] = None
    reason: Optional[str] = None

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "revision_date": self.revision_date,
            "previous_revenue": self.previous_revenue,
            "revised_revenue": self.revised_revenue,
            "previous_operating_income": self.previous_operating_income,
            "revised_operating_income": self.revised_operating_income,
            "previous_net_income": self.previous_net_income,
            "revised_net_income": self.revised_net_income,
            "reason": self.reason
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ForecastRevision":
        """辞書から生成"""
        return cls(
            revision_date=data.get("revision_date"),
            previous_revenue=data.get("previous_revenue"),
            revised_revenue=data.get("revised_revenue"),
            previous_operating_income=data.get("previous_operating_income"),
            revised_operating_income=data.get("revised_operating_income"),
            previous_net_income=data.get("previous_net_income"),
            revised_net_income=data.get("revised_net_income"),
            reason=data.get("reason")
        )


@dataclass
class PerformanceForecast:
    """
    業績予想データ

    Attributes:
        revenue_forecast: 売上高予想（百万円）
        operating_income_forecast: 営業利益予想（百万円）
        net_income_forecast: 当期純利益予想（百万円）
        fiscal_year: 対象会計年度（例: "2024年3月期"）
        revisions: 業績予想の修正履歴リスト
    """
    revenue_forecast: Optional[float] = None
    operating_income_forecast: Optional[float] = None
    net_income_forecast: Optional[float] = None
    fiscal_year: Optional[str] = None
    revisions: List[ForecastRevision] = field(default_factory=list)

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "revenue_forecast": self.revenue_forecast,
            "operating_income_forecast": self.operating_income_forecast,
            "net_income_forecast": self.net_income_forecast,
            "fiscal_year": self.fiscal_year,
            "revisions": [rev.to_dict() for rev in self.revisions]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PerformanceForecast":
        """辞書から生成"""
        revisions_data = data.get("revisions", [])
        revisions = [ForecastRevision.from_dict(rev) for rev in revisions_data] if revisions_data else []

        return cls(
            revenue_forecast=data.get("revenue_forecast"),
            operating_income_forecast=data.get("operating_income_forecast"),
            net_income_forecast=data.get("net_income_forecast"),
            fiscal_year=data.get("fiscal_year"),
            revisions=revisions
        )

    def has_revisions(self) -> bool:
        """修正履歴があるかチェック"""
        return len(self.revisions) > 0
