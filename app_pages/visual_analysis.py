# pages/Visual_Analysis.py
import streamlit as st
from analyze import get_all_assets_changes, get_all_funds_changes
import datetime
import plotly.express as px

def show_visual_analysis():
    st.set_page_config(page_title="Visual Analysis", layout="wide")

    st.title("📊 Visual Analysis")
    st.markdown("Explore your portfolio trends and daily performance at a glance.")

    # --- Date range selection ---
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.date.today())

    if start_date > end_date:
        st.error("Start date cannot be after end date.")
        st.stop()

    # --- Get data ---
    fund_result = get_all_funds_changes(start_date, end_date)
    asset_result = get_all_assets_changes(start_date, end_date)
    if not fund_result or not asset_result:
        st.warning("No data available for the selected date range.")
        st.stop()
    col1, col2 = st.columns(2)
    with col1:
        # --- 1 Daily Total Portfolio Value ---
        st.subheader("Daily Total Portfolio Value (Funds and Assets)")
        st.caption("Shows how your total portfolio value evolved over time.")

        total_df = (fund_result["total_funds"] + asset_result["total_assets"]).reset_index()
        total_df.columns = ["Date", "Total Value (TL)"]
        total_df["Total Value (TL)"] = total_df["Total Value (TL)"].fillna(0)

        fig_total = px.line(
            total_df,
            x="Date",
            y="Total Value (TL)",
            title="Daily Total Portfolio Value",
            markers=True,
        )
        fig_total.update_layout(
            xaxis_title="Date",
            yaxis_title="Total Value (TL)",
            title_x=0.5,
            height=450
        )
        st.plotly_chart(fig_total, use_container_width=True)

        # --- 2 Daily Total Portfolio Value ---
        st.subheader("Daily Total Portfolio Value (Funds only)")
        st.caption("Shows how your funds portfolio value evolved over time.")

        total_df = fund_result["total_funds"].reset_index()
        total_df.columns = ["Date", "Total Funds Value (TL)"]
        total_df["Total Funds Value (TL)"] = total_df["Total Funds Value (TL)"].fillna(0)

        fig_total = px.line(
            total_df,
            x="Date",
            y="Total Funds Value (TL)",
            title="Daily Total Funds Portfolio Value",
            markers=True,
        )
        fig_total.update_layout(
            xaxis_title="Date",
            yaxis_title="Total Funds Value (TL)",
            title_x=0.5,
            height=450
        )
        st.plotly_chart(fig_total, use_container_width=True)
    with col2:    
        # --- 3 Daily Total Portfolio Value ---
        st.subheader("Daily Total Portfolio Value (Assets only)")
        st.caption("Shows how your assets portfolio value evolved over time.")

        total_df = asset_result["total_assets"].reset_index()
        total_df.columns = ["Date", "Total Assets Value (TL)"]
        total_df["Total Assets Value (TL)"] = total_df["Total Assets Value (TL)"].fillna(0)

        fig_total = px.line(
            total_df,
            x="Date",
            y="Total Assets Value (TL)",
            title="Daily Total Assets Portfolio Value",
            markers=True,
        )
        fig_total.update_layout(
            xaxis_title="Date",
            yaxis_title="Total Assets Value (TL)",
            title_x=0.5,
            height=450
        )
        st.plotly_chart(fig_total, use_container_width=True)
        
        # --- 4 Daily Percentage Change ---
        st.subheader("Daily Percentage Change of Total Portfolio")
        st.caption("Shows the daily volatility and direction of change in your total portfolio.")

        pct_df = fund_result["total_pct_change"].reset_index()
        pct_df.columns = ["Date", "Daily % Change"]
        pct_df["Daily % Change"] = pct_df["Daily % Change"].fillna(0)

        fig_pct = px.bar(
            pct_df,
            x="Date",
            y="Daily % Change",
            title="Daily Percentage Change of Total Portfolio",
            color="Daily % Change",
            color_continuous_scale="RdYlGn",
        )
        fig_pct.update_layout(
            xaxis_title="Date",
            yaxis_title="% Change",
            title_x=0.5,
            height=450
        )
        st.plotly_chart(fig_pct, use_container_width=True)

        st.markdown("✅ **Tip:** Green bars indicate gains, red bars indicate losses.")
