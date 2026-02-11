"""
成長性分析モジュール

企業の前期比成長率を計算し、成長性を評価する。
"""

from typing import Dict, Optional
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.income_statement import IncomeStatement


def calculate_growth_rate(current: float, previous: float) -> Optional[float]:
    """
    成長率を計算

    Args:
        current: 当期の値
        previous: 前期の値

    Returns:
        成長率（%）、計算不可の場合はNone

    Formula:
        成長率 = (当期 - 前期) ÷ 前期 × 100
    """
    if previous is None or current is None:
        return None

    if previous == 0:
        # 前期がゼロの場合
        if current > 0:
            return None  # 無限大となるため計算不可
        else:
            return 0.0

    return ((current - previous) / previous) * 100


def evaluate_growth_rate(growth_rate: Optional[float], metric_name: str) -> str:
    """
    成長率を評価してコメントを生成

    Args:
        growth_rate: 成長率（%）
        metric_name: 指標名（売上高、営業利益など）

    Returns:
        評価コメント
    """
    if growth_rate is None:
        return f"{metric_name}の前期比較ができません。"

    if growth_rate >= 10:
        return f"{metric_name}が前期比{growth_rate:.1f}%増と高い成長を示しています。"
    elif growth_rate >= 5:
        return f"{metric_name}が前期比{growth_rate:.1f}%増と順調に成長しています。"
    elif growth_rate > 0:
        return f"{metric_name}が前期比{growth_rate:.1f}%増と微増しています。"
    elif growth_rate == 0:
        return f"{metric_name}は前期と同水準です。"
    elif growth_rate >= -5:
        return f"{metric_name}が前期比{abs(growth_rate):.1f}%減とやや減少しています。"
    elif growth_rate >= -10:
        return f"{metric_name}が前期比{abs(growth_rate):.1f}%減と減少しています。"
    else:
        return f"{metric_name}が前期比{abs(growth_rate):.1f}%減と大きく減少しており、注意が必要です。"


def analyze_growth(
    current_is: IncomeStatement,
    previous_is: Optional[IncomeStatement]
) -> Dict[str, any]:
    """
    成長性分析を実行

    Args:
        current_is: 当期の損益計算書
        previous_is: 前期の損益計算書（Noneの場合は比較なし）

    Returns:
        成長性分析結果
        {
            "has_comparison": bool,  # 前期比較が可能かどうか
            "revenue_growth": float,  # 売上高成長率（%）
            "operating_income_growth": float,  # 営業利益成長率（%）
            "net_income_growth": float,  # 純利益成長率（%）
            "comments": List[str],  # 評価コメントリスト
            "overall_evaluation": str,  # 総合評価
            "message": str  # メッセージ（比較できない場合）
        }
    """
    if previous_is is None:
        return {
            "has_comparison": False,
            "message": "前期データがないため、成長性分析を実施できません。",
            "revenue_growth": None,
            "operating_income_growth": None,
            "net_income_growth": None,
            "comments": [],
            "overall_evaluation": "分析不可"
        }

    # 各指標の成長率を計算
    revenue_growth = calculate_growth_rate(current_is.revenue, previous_is.revenue)
    operating_income_growth = calculate_growth_rate(
        current_is.operating_income,
        previous_is.operating_income
    )
    net_income_growth = calculate_growth_rate(
        current_is.net_income,
        previous_is.net_income
    )

    # 評価コメントを生成
    comments = []

    if revenue_growth is not None:
        comments.append(evaluate_growth_rate(revenue_growth, "売上高"))

    if operating_income_growth is not None:
        comments.append(evaluate_growth_rate(operating_income_growth, "営業利益"))

    if net_income_growth is not None:
        comments.append(evaluate_growth_rate(net_income_growth, "当期純利益"))

    # 総合評価を生成
    overall_evaluation = _generate_overall_evaluation(
        revenue_growth,
        operating_income_growth,
        net_income_growth
    )

    return {
        "has_comparison": True,
        "revenue_growth": revenue_growth,
        "operating_income_growth": operating_income_growth,
        "net_income_growth": net_income_growth,
        "comments": comments,
        "overall_evaluation": overall_evaluation
    }


def _generate_overall_evaluation(
    revenue_growth: Optional[float],
    operating_income_growth: Optional[float],
    net_income_growth: Optional[float]
) -> str:
    """
    総合評価を生成

    Args:
        revenue_growth: 売上高成長率
        operating_income_growth: 営業利益成長率
        net_income_growth: 純利益成長率

    Returns:
        総合評価コメント
    """
    # 成長率の平均を計算（有効なデータのみ）
    valid_rates = [
        rate for rate in [revenue_growth, operating_income_growth, net_income_growth]
        if rate is not None
    ]

    if not valid_rates:
        return "成長性の評価ができません。"

    avg_growth = sum(valid_rates) / len(valid_rates)

    # 増益・減益の判定
    profit_growing = (
        operating_income_growth is not None and operating_income_growth > 0
    ) or (
        net_income_growth is not None and net_income_growth > 0
    )

    profit_declining = (
        operating_income_growth is not None and operating_income_growth < 0
    ) or (
        net_income_growth is not None and net_income_growth < 0
    )

    # 総合評価
    if avg_growth >= 10:
        if profit_growing:
            return "📈 高成長企業：売上・利益ともに高い成長率を示しています。"
        else:
            return "📈 高成長だが収益性に課題：売上は伸びていますが、利益面で改善の余地があります。"
    elif avg_growth >= 5:
        if profit_growing:
            return "✅ 安定成長企業：バランスの取れた成長を遂げています。"
        else:
            return "⚠️ 成長しているが利益減少：売上は伸びていますが、利益が減少しています。"
    elif avg_growth > 0:
        return "➡️ 微増傾向：成長は緩やかですが、前期より改善しています。"
    elif avg_growth > -5:
        return "⚠️ 微減傾向：前期比でやや減少していますが、大きな問題ではありません。"
    else:
        if profit_declining:
            return "❌ 業績悪化：売上・利益ともに減少しており、改善が必要です。"
        else:
            return "⚠️ 減収傾向：売上が減少していますが、利益面では健闘しています。"


if __name__ == "__main__":
    # テスト用コード
    current = IncomeStatement(
        revenue=100000,
        operating_income=15000,
        net_income=10000
    )

    previous = IncomeStatement(
        revenue=90000,
        operating_income=12000,
        net_income=8000
    )

    result = analyze_growth(current, previous)
    print("成長性分析結果:")
    print(f"売上高成長率: {result['revenue_growth']:.2f}%")
    print(f"営業利益成長率: {result['operating_income_growth']:.2f}%")
    print(f"当期純利益成長率: {result['net_income_growth']:.2f}%")
    print("\n評価コメント:")
    for comment in result['comments']:
        print(f"  - {comment}")
    print(f"\n総合評価: {result['overall_evaluation']}")
