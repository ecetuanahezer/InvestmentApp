import streamlit as st
import datetime
import pandas as pd
from analyze import (
    get_all_funds_changes,
    get_all_assets_changes,
    get_portfolio_summary,
    get_top_bottom_funds
)

def show_analysis():
    st.title("📊 Portfolio Analysis")

    # === Date Selection + Summary ===
    col_date, col_summary = st.columns([1.5, 2.5])
    with col_date:
        start_date = st.date_input("Start Date:", datetime.date.today() - datetime.timedelta(days=7), key="start_analysis")
        end_date = st.date_input("End Date:", datetime.date.today(), key="end_analysis")
        show_btn = st.button("Show Analysis")

    with col_summary:
        st.markdown("#### 📘 Summary")
        if not show_btn:
            st.info("🔍 Select a date range and click 'Show Analysis' to view summary.")
        else:
            if start_date > end_date:
                st.error("Start date cannot be after end date.")
                return
            
            # === Get fund + asset data ===
            fund_result = get_all_funds_changes(start_date, end_date)
            asset_result = get_all_assets_changes(start_date, end_date)

            if fund_result is None or asset_result is None:
                st.warning("No data found for the selected period.")
                return
            
            # === Get total summary (fund + assets) ===
            summary = get_portfolio_summary(fund_result, asset_result)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Start Value (TL)", f"{summary['start_value']:,.2f}")
            with col2:
                st.metric("End Value (TL)", f"{summary['end_value']:,.2f}")
            
            st.metric("Total Change", f"{summary['total_change_tl']:,.2f} TL", f"{summary['total_change_pct']:.4f}%")

    # === Analysis Sections ===
    if show_btn:
        if start_date > end_date:
            st.error("Start date cannot be after end date.")
            return

        fund_result = get_all_funds_changes(start_date, end_date)
        asset_result = get_all_assets_changes(start_date, end_date)

        if fund_result is None or asset_result is None:
            st.warning("No data available for this range.")
            return

        # --- Daily Total Values ---
        st.subheader("📅 Daily Total Values (Funds + Assets)")
        
        # Merge indexes to ensure all dates are included
        all_dates = fund_result["total_funds"].index.union(asset_result["total_assets"].index)

        # Fill missing dates with 0
        total_funds = fund_result["total_funds"].reindex(all_dates, fill_value=0)
        total_assets = asset_result["total_assets"].reindex(all_dates, fill_value=0)
        total_funds_pct = fund_result["total_pct_change"].reindex(all_dates, fill_value=0)
        total_assets_pct = asset_result["total_pct_change"].reindex(all_dates, fill_value=0)
        total_sum = total_funds + total_assets
        total_sum_pct_change = total_sum.pct_change().fillna(0)

        df_total = pd.DataFrame({
            "Date": all_dates,
            "TOTAL (TL)": total_sum.round(2).astype(str) + " TL (" + total_sum_pct_change.round(2).astype(str) + "%)",
            "Total Funds (TL)": total_funds.round(2).astype(str) + " TL (" + total_funds_pct.round(2).astype(str) + "%)",
            "Total Assets (TL)": total_assets.round(2).astype(str) + " TL (" + total_assets_pct.round(2).astype(str) + "%)",
            "Precious Metals (TL)": asset_result["pivot"]["precious_metals_tl"].reindex(all_dates, fill_value=0).round(2).astype(str) + " TL (" +
                                    asset_result["asset_pct_changes"]["precious_metals_tl"].reindex(all_dates, fill_value=0).round(2).astype(str) + "%)",
            "Crypto (TL)": asset_result["pivot"]["crypto_tl"].reindex(all_dates, fill_value=0).round(2).astype(str) + " TL (" +
                        asset_result["asset_pct_changes"]["crypto_tl"].reindex(all_dates, fill_value=0).round(2).astype(str) + "%)",
            "Physical Gold (TL)": asset_result["pivot"]["physical_gold_tl"].reindex(all_dates, fill_value=0).round(2).astype(str) + " TL (" +
                                asset_result["asset_pct_changes"]["physical_gold_tl"].reindex(all_dates, fill_value=0).round(2).astype(str) + "%)",
        }).set_index("Date")

        st.dataframe(df_total.round(2), use_container_width=True)

        # --- Daily Fund Changes ---
        st.subheader("📈 Daily Fund Changes")
        df_fund_changes = fund_result["fund_changes"].round(2)
        df_fund_pct = fund_result["fund_pct_changes"].round(2)

        df_display_fund = pd.DataFrame(index=df_fund_changes.index)
        for col in df_fund_changes.columns:
            df_display_fund[col] = (
                df_fund_changes[col].astype(str) + " TL (" + df_fund_pct[col].astype(str) + "%)"
            )

        st.dataframe(df_display_fund, use_container_width=True)

        # --- Daily Asset Changes ---
        st.subheader("💰 Daily Asset Changes")
        df_asset_changes = asset_result["asset_changes"].round(2)
        df_asset_pct = asset_result["asset_pct_changes"].round(2)

        df_display_asset = pd.DataFrame(index=df_asset_changes.index)
        for col in df_asset_changes.columns:
            df_display_asset[col] = (
                df_asset_changes[col].astype(str) + " TL (" + df_asset_pct[col].astype(str) + "%)"
            )

        st.dataframe(df_display_asset, use_container_width=True)

        # --- Top / Bottom Funds ---
        st.subheader("🏆 Top / Bottom Funds (Overall Period)")
        top_funds_by_pct, top_funds_by_tl, bottom_funds_by_pct, bottom_funds_by_tl = get_top_bottom_funds(fund_result)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Top 5 by Gain:**")
            st.table(top_funds_by_pct.reset_index().rename(columns={"index": "Fund Code", 0: "% Change"}).round(2))
            st.table(top_funds_by_tl.reset_index().rename(columns={"index": "Fund Code", 0: "TL Change"}).round(2))


        with col2:
            st.markdown("**Bottom 5 by Loss:**")
            st.table(bottom_funds_by_pct.reset_index().rename(columns={"index": "Fund Code", 0: "% Change"}).round(2))
            st.table(bottom_funds_by_tl.reset_index().rename(columns={"index": "Fund Code", 0: "TL Change"}).round(2))
