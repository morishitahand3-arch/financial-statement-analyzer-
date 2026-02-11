"""
セグメント情報データモデル

事業セグメント別の業績データを格納する。
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Segment:
    """
    個別セグメントデータ

    Attributes:
        name: セグメント名（例: "デジタルサービス事業"）
        revenue: セグメント売上高（百万円）
        operating_income: セグメント営業利益（百万円）
    """
    name: str
    revenue: float = 0.0
    operating_income: Optional[float] = None

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "name": self.name,
            "revenue": self.revenue,
            "operating_income": self.operating_income
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Segment":
        """辞書から生成"""
        return cls(
            name=data.get("name", ""),
            revenue=data.get("revenue", 0.0),
            operating_income=data.get("operating_income")
        )

    def calculate_margin(self) -> Optional[float]:
        """
        営業利益率を計算

        Returns:
            営業利益率（%）、データがない場合はNone
        """
        if self.operating_income is None or self.revenue == 0:
            return None
        return (self.operating_income / self.revenue) * 100


@dataclass
class SegmentAnalysis:
    """
    セグメント分析データ

    Attributes:
        segments: セグメントリスト
        total_revenue: 全セグメント合計売上高（百万円）
        fiscal_year: 対象会計年度（例: "2024年3月期"）
    """
    segments: List[Segment]
    total_revenue: float
    fiscal_year: Optional[str] = None

    def __post_init__(self):
        """合計売上高を自動計算（提供されていない場合）"""
        if self.total_revenue == 0 and self.segments:
            self.total_revenue = sum(seg.revenue for seg in self.segments)

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "segments": [seg.to_dict() for seg in self.segments],
            "total_revenue": self.total_revenue,
            "fiscal_year": self.fiscal_year
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SegmentAnalysis":
        """辞書から生成"""
        segments = [Segment.from_dict(seg) for seg in data.get("segments", [])]
        return cls(
            segments=segments,
            total_revenue=data.get("total_revenue", 0),
            fiscal_year=data.get("fiscal_year")
        )

    def get_segment_ratio(self, segment_name: str) -> Optional[float]:
        """
        特定セグメントの構成比を計算

        Args:
            segment_name: セグメント名

        Returns:
            構成比（%）、見つからない場合はNone
        """
        if self.total_revenue == 0:
            return None

        for seg in self.segments:
            if seg.name == segment_name:
                return (seg.revenue / self.total_revenue) * 100
        return None

    def get_largest_segment(self) -> Optional[Segment]:
        """
        最大のセグメント（売上高ベース）を取得

        Returns:
            最大セグメント、データがない場合はNone
        """
        if not self.segments:
            return None
        return max(self.segments, key=lambda seg: seg.revenue)

    def get_segments_by_revenue_desc(self) -> List[Segment]:
        """
        売上高の大きい順にセグメントを取得

        Returns:
            売上高降順のセグメントリスト
        """
        return sorted(self.segments, key=lambda seg: seg.revenue, reverse=True)
