# analyze.py
# Analyze all funds changes
import numpy as np
from database import AssetValue, FundValue, SessionLocal
from sqlalchemy import and_
import pandas as pd


def get_all_funds_changes(start_date, end_date):
    """
    Returns the changes of all funds within the selected date range.
    - Daily TL and % changes for each fund
    - Total portfolio change in TL and % (based on first and last date only)
    - Top 5 performing funds (by TL and %)
    - Bottom 5 performing funds (by TL and %)
    """
    session = SessionLocal()

    # Query all data within the specified date range
    query = (
        session.query(FundValue.date, FundValue.fund_code, FundValue.value_tl)
        .filter(and_(FundValue.date >= start_date, FundValue.date <= end_date))
        .order_by(FundValue.date)
        .all()
    )
    session.close()

    if not query:
        print("❌ No data available for the selected date range.")
        return None

    df = pd.DataFrame(query, columns=["date", "fund_code", "value_tl"])

    # Pivot table: rows = date, columns = fund code
    pivot = (
        df.pivot(index="date", columns="fund_code", values="value_tl")
        .sort_index()
        .fillna(0)
    )

    # Daily changes for each fund
    fund_changes = pivot.diff().fillna(0)
    fund_pct_changes = (pivot.pct_change().replace([np.inf, -np.inf], 0) * 100).fillna(
        0
    )
    total = pivot.sum(axis=1).fillna(0)
    total_funds_change = total.diff().fillna(0)
    total_pct_change = (total.pct_change().replace([np.inf, -np.inf], 0) * 100).fillna(
        0
    )

    result = {
        "pivot": pivot,
        "fund_changes": fund_changes,
        "fund_pct_changes": fund_pct_changes,
        "total_funds": total,
        "total_funds_change": total_funds_change,
        "total_pct_change": total_pct_change,
    }

    return result


def get_all_assets_changes(start_date, end_date):
    """
    Returns the daily TL and % changes for all asset categories:
    - precious_metals_tl
    - crypto_tl
    - physical_gold_tl
    """
    session = SessionLocal()

    query = (
        session.query(
            AssetValue.date,
            AssetValue.precious_metals_tl,
            AssetValue.crypto_tl,
            AssetValue.physical_gold_tl,
        )
        .filter(and_(AssetValue.date >= start_date, AssetValue.date <= end_date))
        .order_by(AssetValue.date)
        .all()
    )
    session.close()

    if not query:
        print("❌ No asset data available for the selected date range.")
        return None

    df = (
        pd.DataFrame(
            query,
            columns=["date", "precious_metals_tl", "crypto_tl", "physical_gold_tl"],
        )
        .set_index("date")
        .fillna(0)
        .sort_index()
    )

    # Daily TL and % changes
    asset_changes = df.diff().fillna(0)
    asset_pct_changes = (df.pct_change().replace([np.inf, -np.inf], 0) * 100).fillna(0)
    total = df.sum(axis=1).fillna(0)
    total_assets_change = total.diff().fillna(0)
    total_pct_change = (total.pct_change().replace([np.inf, -np.inf], 0) * 100).fillna(
        0
    )
    result = {
        "pivot": df,  # TL values per category
        "asset_changes": asset_changes,  # Daily TL changes
        "asset_pct_changes": asset_pct_changes,  # Daily % changes
        "total_assets": total,  # Total asset value per day
        "total_assets_change": total_assets_change,  # Daily TL change of total assets
        "total_pct_change": total_pct_change,  # Daily % change of total assets
    }

    return result


def get_top_bottom_funds(fund_result, top_n=5):
    """
    Calculates top and bottom performing funds by % change
    over the selected period.
    """

    if fund_result is None:
        return None, None

    # Get start and end values
    start_values = fund_result["pivot"].iloc[0]
    end_values = fund_result["pivot"].iloc[-1]

    # Calculate % changes
    pct_changes = ((end_values - start_values) / start_values) * 100
    change_tl = end_values - start_values
    # Find top and bottom funds
    top_funds_by_pct = pct_changes.sort_values(ascending=False).head(top_n)
    top_funds_by_tl = change_tl.sort_values(ascending=False).head(top_n)
    bottom_funds_by_pct = pct_changes.sort_values(ascending=True).head(top_n)
    bottom_funds_by_tl = change_tl.sort_values(ascending=True).head(top_n)
    return top_funds_by_pct, top_funds_by_tl, bottom_funds_by_pct, bottom_funds_by_tl
