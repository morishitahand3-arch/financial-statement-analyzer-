"""
セグメント分析モジュール

事業セグメント別の売上構成比、利益率などを分析する。
"""

from typing import Dict, List, Optional
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.segment import SegmentAnalysis, Segment


def calculate_segment_ratio(segment_revenue: float, total_revenue: float) -> Optional[float]:
    """
    セグメント構成比を計算

    Args:
        segment_revenue: セグメント売上高
        total_revenue: 全セグメント合計売上高

    Returns:
        構成比（%）、計算不可の場合はNone
    """
    if total_revenue == 0 or segment_revenue is None:
        return None

    return (segment_revenue / total_revenue) * 100


def analyze_segments(segment_analysis: SegmentAnalysis) -> Dict[str, any]:
    """
    セグメント分析を実行

    Args:
        segment_analysis: セグメント分析データ

    Returns:
        セグメント分析結果
        {
            "segments": List[dict],  # セグメント詳細リスト
            "dominant_segment": dict,  # 主力セグメント
            "segment_count": int,  # セグメント数
            "concentration_ratio": float,  # 主力セグメントの集中度
            "comments": List[str]  # 評価コメント
        }
    """
    if not segment_analysis or not segment_analysis.segments:
        return {
            "has_segments": False,
            "message": "セグメント情報が抽出されていません。"
        }

    segments = segment_analysis.segments
    total_revenue = segment_analysis.total_revenue

    # 各セグメントの詳細を計算
    segment_details = []
    for seg in segments:
        ratio = calculate_segment_ratio(seg.revenue, total_revenue)
        margin = seg.calculate_margin()

        segment_details.append({
            "name": seg.name,
            "revenue": seg.revenue,
            "operating_income": seg.operating_income,
            "ratio": ratio,
            "margin": margin
        })

    # 売上高で降順ソート
    segment_details.sort(key=lambda x: x["revenue"], reverse=True)

    # 主力セグメント（最大のセグメント）
    dominant_segment = segment_details[0] if segment_details else None

    # 主力セグメントの集中度
    concentration_ratio = dominant_segment["ratio"] if dominant_segment else None

    # 評価コメントを生成
    comments = _generate_segment_comments(
        segment_details,
        dominant_segment,
        concentration_ratio
    )

    return {
        "has_segments": True,
        "segments": segment_details,
        "dominant_segment": dominant_segment,
        "segment_count": len(segments),
        "concentration_ratio": concentration_ratio,
        "comments": comments
    }


def _generate_segment_comments(
    segments: List[Dict],
    dominant_segment: Optional[Dict],
    concentration_ratio: Optional[float]
) -> List[str]:
    """
    セグメント分析の評価コメントを生成

    Args:
        segments: セグメント詳細リスト
        dominant_segment: 主力セグメント
        concentration_ratio: 集中度

    Returns:
        評価コメントリスト
    """
    comments = []

    if not segments:
        return comments

    # 主力セグメントの評価
    if dominant_segment:
        comments.append(
            f"主力セグメントは「{dominant_segment['name']}」で、"
            f"全体の{concentration_ratio:.1f}%を占めています。"
        )

    # 集中度の評価
    if concentration_ratio:
        if concentration_ratio >= 70:
            comments.append(
                "特定セグメントへの集中度が高く、依存リスクがあります。"
            )
        elif concentration_ratio >= 50:
            comments.append(
                "主力セグメントの比率が高めですが、バランスは取れています。"
            )
        else:
            comments.append(
                "複数セグメントでバランス良く売上を構成しています。"
            )

    # 利益率の評価
    segments_with_margin = [s for s in segments if s.get("margin") is not None]
    if segments_with_margin:
        highest_margin_seg = max(segments_with_margin, key=lambda x: x["margin"])
        comments.append(
            f"営業利益率が最も高いのは「{highest_margin_seg['name']}」"
            f"（{highest_margin_seg['margin']:.1f}%）です。"
        )

    # セグメント数の評価
    segment_count = len(segments)
    if segment_count >= 5:
        comments.append(
            f"{segment_count}つのセグメントで事業を展開しており、"
            "事業の多角化が進んでいます。"
        )
    elif segment_count >= 3:
        comments.append(
            f"{segment_count}つの主要セグメントで事業を展開しています。"
        )
    else:
        comments.append(
            f"{segment_count}つのセグメントに絞って事業を展開しています。"
        )

    return comments


if __name__ == "__main__":
    # テスト用コード
    segments = [
        Segment(name="デジタルサービス事業", revenue=50000, operating_income=8000),
        Segment(name="コンサルティング事業", revenue=30000, operating_income=5000),
        Segment(name="製品販売事業", revenue=20000, operating_income=2000),
    ]

    segment_analysis = SegmentAnalysis(
        segments=segments,
        total_revenue=100000,
        fiscal_year="2024年3月期"
    )

    result = analyze_segments(segment_analysis)

    if result.get("has_segments"):
        print("セグメント分析結果:")
        print(f"セグメント数: {result['segment_count']}")
        print(f"\n主力セグメント: {result['dominant_segment']['name']}")
        print(f"集中度: {result['concentration_ratio']:.1f}%")

        print("\n各セグメント:")
        for seg in result['segments']:
            print(f"  {seg['name']}")
            print(f"    売上高: {seg['revenue']:,.0f}百万円 ({seg['ratio']:.1f}%)")
            if seg['margin'] is not None:
                print(f"    営業利益率: {seg['margin']:.1f}%")

        print("\n評価コメント:")
        for comment in result['comments']:
            print(f"  - {comment}")
