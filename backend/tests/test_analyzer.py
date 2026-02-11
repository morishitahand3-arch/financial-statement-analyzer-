"""
財務分析のテスト
"""
import pytest
from backend.models.balance_sheet import BalanceSheet
from backend.models.income_statement import IncomeStatement
from backend.analyzers.profitability import (
    calculate_roe,
    calculate_roa,
    calculate_operating_margin,
)
from backend.analyzers.safety import (
    calculate_equity_ratio,
    calculate_current_ratio,
    calculate_fixed_ratio,
)


class TestProfitabilityAnalysis:
    """収益性分析のテスト"""

    def test_calculate_roe(self):
        """ROE計算のテスト"""
        balance_sheet = BalanceSheet(
            total_assets=1000000,
            total_liabilities=600000,
            total_net_assets=400000,
            shareholders_equity=400000,
            current_assets=600000,
            fixed_assets=400000,
        )
        income_statement = IncomeStatement(
            revenue=500000, operating_income=50000, net_income=30000
        )

        roe = calculate_roe(income_statement, balance_sheet)
        assert roe == 7.5  # (30000 / 400000) * 100

    def test_calculate_roa(self):
        """ROA計算のテスト"""
        balance_sheet = BalanceSheet(
            total_assets=1000000,
            total_liabilities=600000,
            total_net_assets=400000,
            shareholders_equity=400000,
            current_assets=600000,
            fixed_assets=400000,
        )
        income_statement = IncomeStatement(
            revenue=500000, operating_income=50000, net_income=30000
        )

        roa = calculate_roa(income_statement, balance_sheet)
        assert roa == 3.0  # (30000 / 1000000) * 100

    def test_calculate_operating_margin(self):
        """営業利益率計算のテスト"""
        income_statement = IncomeStatement(
            revenue=500000, operating_income=50000, net_income=30000
        )

        margin = calculate_operating_margin(income_statement)
        assert margin == 10.0  # (50000 / 500000) * 100


class TestSafetyAnalysis:
    """安全性分析のテスト"""

    def test_calculate_equity_ratio(self):
        """自己資本比率計算のテスト"""
        balance_sheet = BalanceSheet(
            total_assets=1000000,
            total_liabilities=600000,
            total_net_assets=400000,
            shareholders_equity=400000,
            current_assets=600000,
            fixed_assets=400000,
        )

        ratio = calculate_equity_ratio(balance_sheet)
        assert ratio == 40.0  # (400000 / 1000000) * 100

    def test_calculate_current_ratio(self):
        """流動比率計算のテスト"""
        balance_sheet = BalanceSheet(
            total_assets=1000000,
            total_liabilities=600000,
            total_net_assets=400000,
            shareholders_equity=400000,
            current_assets=600000,
            fixed_assets=400000,
            current_liabilities=300000,
        )

        ratio = calculate_current_ratio(balance_sheet)
        assert ratio == 200.0  # (600000 / 300000) * 100

    def test_calculate_fixed_ratio(self):
        """固定比率計算のテスト"""
        balance_sheet = BalanceSheet(
            total_assets=1000000,
            total_liabilities=600000,
            total_net_assets=400000,
            shareholders_equity=400000,
            current_assets=600000,
            fixed_assets=400000,
        )

        ratio = calculate_fixed_ratio(balance_sheet)
        assert ratio == 100.0  # (400000 / 400000) * 100
