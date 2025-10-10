# analyze.py
# Analyze all funds changes
from database import FundValue, SessionLocal
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
    query = session.query(FundValue.date, FundValue.fund_code, FundValue.value_tl)\
        .filter(and_(FundValue.date >= start_date, FundValue.date <= end_date))\
        .order_by(FundValue.date).all()
    session.close()

    if not query:
        print("❌ No data available for the selected date range.")
        return None

    df = pd.DataFrame(query, columns=["date", "fund_code", "value_tl"])
    
    # Pivot table: rows = date, columns = fund code
    pivot = df.pivot(index="date", columns="fund_code", values="value_tl").sort_index()
    
    # Daily changes for each fund
    fund_changes = pivot.diff().fillna(0)
    fund_pct_changes = (pivot.pct_change() * 100).fillna(0)

    # Total portfolio per day (sum of all funds)
    total = pivot.sum(axis=1)
    total_change = total.diff().fillna(0)
    total_pct_change = total.pct_change() * 100

    # -------------------
    # Summary calculations
    # -------------------
    first_values = pivot.iloc[0]
    last_values = pivot.iloc[-1]

    # Total TL and % change per fund (first vs last date)
    fund_total_change_tl = last_values - first_values
    fund_total_change_pct = ((last_values - first_values) / first_values) * 100

    # Total portfolio summary change
    total_change_tl_summary = fund_total_change_tl.sum()
    total_change_pct_summary = (last_values.sum() - first_values.sum()) / first_values.sum() * 100

    # Top 5 performing funds
    top5_pct = fund_total_change_pct.sort_values(ascending=False).head(5)
    top5_tl = fund_total_change_tl.sort_values(ascending=False).head(5)

    # Bottom 5 performing funds
    bottom5_pct = fund_total_change_pct.sort_values().head(5)
    bottom5_tl = fund_total_change_tl.sort_values().head(5)

    result = {
        "pivot": pivot,                         # TL values for each fund
        "fund_changes": fund_changes,           # Daily TL change per fund
        "fund_pct_changes": fund_pct_changes,   # Daily % change per fund
        "total": total,                         # Total portfolio TL per day
        "total_change": total_change,           # Daily portfolio TL change
        "total_pct_change": total_pct_change,   # Daily portfolio % change
        # Summary
        "fund_total_change_tl": fund_total_change_tl,     # Total TL change per fund
        "fund_total_change_pct": fund_total_change_pct,   # Total % change per fund
        "total_change_tl_summary": total_change_tl_summary,   # Total portfolio TL change summary
        "total_change_pct_summary": total_change_pct_summary, # Total portfolio % change summary
        "top5_pct": top5_pct,                     # Top 5 funds by % change
        "top5_tl": top5_tl,                       # Top 5 funds by TL change
        "bottom5_pct": bottom5_pct,               # Bottom 5 funds by % change
        "bottom5_tl": bottom5_tl                  # Bottom 5 funds by TL change
    }
    
    return result
