"""
業績予想比較分析モジュール

実績と業績予想を比較し、達成率を計算する。
"""

from typing import Dict, Optional, Tuple
import sys
import re
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.income_statement import IncomeStatement
from models.forecast import PerformanceForecast


def extract_quarter_info(fiscal_year: Optional[str]) -> Tuple[Optional[int], int]:
    """
    会計年度から四半期情報を抽出

    Args:
        fiscal_year: 会計年度文字列（例: "2026年3月期第3四半期"）

    Returns:
        (四半期番号, 経過月数)のタプル
        四半期情報がない場合は(None, 12)を返す（通期とみなす）

    Examples:
        "2026年3月期第3四半期" -> (3, 9)
        "2026年3月期" -> (None, 12)
    """
    if not fiscal_year:
        return None, 12

    # 四半期パターンのマッチング
    quarter_patterns = [
        r'第(\d)四半期',
        r'Q(\d)',
        r'(\d)Q',
    ]

    for pattern in quarter_patterns:
        match = re.search(pattern, fiscal_year)
        if match:
            quarter = int(match.group(1))
            elapsed_months = quarter * 3
            return quarter, elapsed_months

    # 四半期情報がない場合は通期とみなす
    return None, 12


def calculate_achievement_rate(actual: float, forecast: float) -> Optional[float]:
    """
    達成率を計算

    Args:
        actual: 実績値
        forecast: 予想値

    Returns:
        達成率（%）、計算不可の場合はNone

    Formula:
        達成率 = 実績 ÷ 予想 × 100
    """
    if forecast is None or actual is None:
        return None

    if forecast == 0:
        return None

    return (actual / forecast) * 100


def evaluate_achievement_rate(
    achievement_rate: Optional[float],
    metric_name: str,
    quarter: Optional[int] = None,
    elapsed_months: int = 12
) -> Dict[str, any]:
    """
    達成率を評価（四半期を考慮）

    Args:
        achievement_rate: 達成率（%）
        metric_name: 指標名
        quarter: 四半期番号（1-4）、通期の場合はNone
        elapsed_months: 経過月数（デフォルト: 12）

    Returns:
        評価結果
        {
            "status": str,  # "excellent", "good", "fair", "poor"
            "comment": str,  # 評価コメント
            "color_class": str  # CSS用のクラス名
        }
    """
    if achievement_rate is None:
        return {
            "status": "unknown",
            "comment": f"{metric_name}の予想データがありません。",
            "color_class": "achievement-unknown"
        }

    # 四半期の場合は期待進捗率を計算
    if quarter is not None:
        expected_progress = (elapsed_months / 12) * 100

        # 期待進捗率に対する実際の達成率
        # 例: 3Q（75%期待）で達成率70%なら、期待に対して93%の進捗
        relative_achievement = (achievement_rate / expected_progress) * 100

        # 四半期用の評価基準
        if relative_achievement >= 95:
            return {
                "status": "excellent",
                "comment": f"{metric_name}は通期予想に対して{achievement_rate:.1f}%の進捗です。第{quarter}四半期時点としては順調に推移しています。",
                "color_class": "achievement-high"
            }
        elif relative_achievement >= 85:
            return {
                "status": "good",
                "comment": f"{metric_name}は通期予想に対して{achievement_rate:.1f}%の進捗です。第{quarter}四半期時点としてはおおむね順調です。",
                "color_class": "achievement-high"
            }
        elif relative_achievement >= 75:
            return {
                "status": "fair",
                "comment": f"{metric_name}は通期予想に対して{achievement_rate:.1f}%の進捗です。第{quarter}四半期時点としてはやや遅れています。",
                "color_class": "achievement-medium"
            }
        else:
            return {
                "status": "poor",
                "comment": f"{metric_name}は通期予想に対して{achievement_rate:.1f}%の進捗です。第{quarter}四半期時点として大幅に遅れており、通期達成が困難な可能性があります。",
                "color_class": "achievement-low"
            }

    # 通期の場合は従来の評価基準
    if achievement_rate >= 100:
        return {
            "status": "excellent",
            "comment": f"{metric_name}は予想を達成しています（達成率: {achievement_rate:.1f}%）。",
            "color_class": "achievement-high"
        }
    elif achievement_rate >= 90:
        return {
            "status": "good",
            "comment": f"{metric_name}は予想にほぼ届いています（達成率: {achievement_rate:.1f}%）。",
            "color_class": "achievement-high"
        }
    elif achievement_rate >= 80:
        return {
            "status": "fair",
            "comment": f"{metric_name}は予想を下回っています（達成率: {achievement_rate:.1f}%）。",
            "color_class": "achievement-medium"
        }
    else:
        return {
            "status": "poor",
            "comment": f"{metric_name}は予想を大きく下回っており、改善が必要です（達成率: {achievement_rate:.1f}%）。",
            "color_class": "achievement-low"
        }


def analyze_forecast_comparison(
    income_statement: IncomeStatement,
    forecast: PerformanceForecast
) -> Dict[str, any]:
    """
    業績予想比較分析を実行

    Args:
        income_statement: 実績の損益計算書
        forecast: 業績予想データ

    Returns:
        業績予想比較分析結果
        {
            "has_forecast": bool,  # 予想データがあるかどうか
            "revenue": {
                "actual": float,
                "forecast": float,
                "achievement_rate": float,
                "evaluation": dict
            },
            "operating_income": {...},
            "net_income": {...},
            "overall_evaluation": str,
            "message": str  # 予想データがない場合のメッセージ
        }
    """
    if forecast is None:
        return {
            "has_forecast": False,
            "message": "業績予想データがないため、比較分析を実施できません。"
        }

    # 四半期情報を抽出
    quarter, elapsed_months = extract_quarter_info(income_statement.fiscal_year)

    # 売上高の達成率
    revenue_achievement = calculate_achievement_rate(
        income_statement.revenue,
        forecast.revenue_forecast
    )
    revenue_eval = evaluate_achievement_rate(
        revenue_achievement, "売上高", quarter, elapsed_months
    )

    # 営業利益の達成率
    operating_income_achievement = calculate_achievement_rate(
        income_statement.operating_income,
        forecast.operating_income_forecast
    )
    operating_income_eval = evaluate_achievement_rate(
        operating_income_achievement, "営業利益", quarter, elapsed_months
    )

    # 当期純利益の達成率
    net_income_achievement = calculate_achievement_rate(
        income_statement.net_income,
        forecast.net_income_forecast
    )
    net_income_eval = evaluate_achievement_rate(
        net_income_achievement, "当期純利益", quarter, elapsed_months
    )

    # 総合評価を生成
    overall_evaluation = _generate_overall_evaluation(
        revenue_eval,
        operating_income_eval,
        net_income_eval
    )

    # 修正履歴を辞書形式に変換
    revisions = [rev.to_dict() for rev in forecast.revisions] if forecast.revisions else []

    return {
        "has_forecast": True,
        "quarter_info": {
            "quarter": quarter,
            "elapsed_months": elapsed_months,
            "is_interim": quarter is not None
        },
        "revenue": {
            "actual": income_statement.revenue,
            "forecast": forecast.revenue_forecast,
            "achievement_rate": revenue_achievement,
            "evaluation": revenue_eval
        },
        "operating_income": {
            "actual": income_statement.operating_income,
            "forecast": forecast.operating_income_forecast,
            "achievement_rate": operating_income_achievement,
            "evaluation": operating_income_eval
        },
        "net_income": {
            "actual": income_statement.net_income,
            "forecast": forecast.net_income_forecast,
            "achievement_rate": net_income_achievement,
            "evaluation": net_income_eval
        },
        "overall_evaluation": overall_evaluation,
        "revisions": revisions
    }


def _generate_overall_evaluation(
    revenue_eval: Dict,
    operating_income_eval: Dict,
    net_income_eval: Dict
) -> str:
    """
    総合評価を生成

    Args:
        revenue_eval: 売上高の評価
        operating_income_eval: 営業利益の評価
        net_income_eval: 当期純利益の評価

    Returns:
        総合評価コメント
    """
    # ステータスの集計
    statuses = [
        revenue_eval["status"],
        operating_income_eval["status"],
        net_income_eval["status"]
    ]

    excellent_count = statuses.count("excellent")
    good_count = statuses.count("good")
    fair_count = statuses.count("fair")
    poor_count = statuses.count("poor")

    # 総合評価
    if excellent_count >= 2:
        return "🎯 優良：業績予想を達成または上回っており、計画通りの業績を上げています。"
    elif excellent_count + good_count >= 2:
        return "✅ 良好：業績予想におおむね沿った実績を残しています。"
    elif poor_count >= 2:
        return "❌ 要改善：業績予想を大きく下回っており、経営戦略の見直しが必要です。"
    elif fair_count >= 2:
        return "⚠️ 注意：業績予想を下回っており、今後の改善が求められます。"
    else:
        return "➡️ 標準：業績予想に対する達成度は標準的なレベルです。"


if __name__ == "__main__":
    # テスト用コード
    actual_is = IncomeStatement(
        revenue=95000,
        operating_income=14000,
        net_income=9500
    )

    forecast_data = PerformanceForecast(
        revenue_forecast=100000,
        operating_income_forecast=15000,
        net_income_forecast=10000,
        fiscal_year="2024年3月期"
    )

    result = analyze_forecast_comparison(actual_is, forecast_data)

    if result.get("has_forecast"):
        print("業績予想比較分析結果:")
        print(f"\n売上高:")
        print(f"  実績: {result['revenue']['actual']:,.0f}百万円")
        print(f"  予想: {result['revenue']['forecast']:,.0f}百万円")
        print(f"  達成率: {result['revenue']['achievement_rate']:.1f}%")
        print(f"  評価: {result['revenue']['evaluation']['comment']}")

        print(f"\n営業利益:")
        print(f"  実績: {result['operating_income']['actual']:,.0f}百万円")
        print(f"  予想: {result['operating_income']['forecast']:,.0f}百万円")
        print(f"  達成率: {result['operating_income']['achievement_rate']:.1f}%")
        print(f"  評価: {result['operating_income']['evaluation']['comment']}")

        print(f"\n総合評価: {result['overall_evaluation']}")
