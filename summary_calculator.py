import pandas as pd


class SummaryCalculator:
    """
    A class to calculate summary statistics for funds, assets, and overall portfolio.
    It provides methods to compute start value, end value, total change in TL and percentage.
    """

    @staticmethod
    def _calculate(series):
        if series is None or series.empty:
            return None

        start_value = series.iloc[0]
        end_value = series.iloc[-1]
        total_change_tl = end_value - start_value
        total_change_pct = (
            (total_change_tl / start_value * 100) if start_value != 0 else 0
        )

        return {
            "start_value": start_value,
            "end_value": end_value,
            "total_change_tl": total_change_tl,
            "total_change_pct": total_change_pct,
        }

    @staticmethod
    def from_fund(fund_result):
        if fund_result is None:
            return None
        return SummaryCalculator._calculate(fund_result["total_funds"])

    @staticmethod
    def from_asset(asset_result, column_name):
        if asset_result is None:
            return None
        return SummaryCalculator._calculate(asset_result["pivot"][column_name])

    @staticmethod
    def from_portfolio(fund_result, asset_result):
        if fund_result is None and asset_result is None:
            return None

        fund_total = (
            fund_result["total_funds"] if fund_result else pd.Series(dtype=float)
        )
        asset_total = (
            asset_result["pivot"].sum(axis=1)
            if asset_result
            else pd.Series(0, index=fund_total.index)
        )

        combined = pd.concat([fund_total, asset_total], axis=1).fillna(0)
        combined.columns = ["funds", "assets"]
        combined["total_portfolio"] = combined["funds"] + combined["assets"]

        summary = SummaryCalculator._calculate(combined["total_portfolio"])
        if summary is not None:
            summary["daily_total"] = combined
        return summary
