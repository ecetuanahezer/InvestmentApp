# app.py
import streamlit as st
import datetime
from io import StringIO
from ingest_data import parse_and_save
from analyze import get_all_funds_changes
import os
import pandas as pd

# --- Title ---
st.title("Investment Funds Tracking App")

# --- Fund Data Upload ---
st.header("📥 Upload Fund Data")
upload_date_fund = st.date_input("Select fund data date:", datetime.date.today(), key="fund_date")

uploaded_file = st.file_uploader("Upload a text file (.txt)", type=["txt"], key="fund_file")
text_input = st.text_area("Or paste the data here (funds and values, tab-separated, 2 lines):", key="fund_text")

if st.button("Upload Fund Data"):
    if uploaded_file is not None:
        content_bytes = uploaded_file.getvalue()
        content_str = content_bytes.decode("utf-8")
        parse_and_save(StringIO(content_str), upload_date_fund)

        # Save to data folder
        os.makedirs("data", exist_ok=True)
        file_path = f"data/{upload_date_fund}.txt"
        with open(file_path, "wb") as f:
            f.write(content_bytes)

        st.success(f"Fund data for {upload_date_fund} uploaded and saved to data folder.")

    elif text_input.strip() != "":
        parse_and_save(StringIO(text_input), upload_date_fund)

        os.makedirs("data", exist_ok=True)
        file_path = f"data/{upload_date_fund}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_input)

        st.success(f"Fund data for {upload_date_fund} uploaded and saved to data folder.")

    else:
        st.warning("Please upload a file or paste the data in the text area.")

# --- Other Assets Input ---
st.header("💰 Other Assets Input (TL)")
upload_date_assets = st.date_input("Select other assets date:", datetime.date.today(), key="asset_date")
metal = st.number_input("Precious Metals (TL)", min_value=0.0, step=1.0)
crypto = st.number_input("Crypto (TL)", min_value=0.0, step=1.0)
physical_gold = st.number_input("Physical Gold (TL)", min_value=0.0, step=1.0)

if st.button("Save Other Assets"):
    # Create folder if it doesn't exist
    os.makedirs("data_assets", exist_ok=True)
    file_path = f"data_assets/{upload_date_assets}.txt"
    
    # Save file (tab-separated single line)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"{metal}\t{crypto}\t{physical_gold}")
    
    st.success(f"Other assets for {upload_date_assets} saved to data_assets folder.")

# --- Analysis Table ---
st.header("📊 Analysis and Daily Values")
start_date = st.date_input("Start Date:", datetime.date.today() - datetime.timedelta(days=7), key="start_analysis")
end_date = st.date_input("End Date:", datetime.date.today(), key="end_analysis")

if st.button("Show Analysis"):
    if start_date > end_date:
        st.error("Start date cannot be after end date.")
    else:
        result = get_all_funds_changes(start_date, end_date)
        if result is not None:
            # --- Daily Fund Changes ---
            st.subheader("🔹 Daily Fund Changes")
            df_table = result["fund_changes"].copy()
            df_pct = result["fund_pct_changes"].copy()

            # TOTAL columns first
            daily_total = result["pivot"].sum(axis=1)
            total_change = result["total_change"]
            total_pct_change = result["total_pct_change"]

            df_display = pd.DataFrame(index=df_table.index)
            df_display["TOTAL_TL"] = daily_total.round(2)
            df_display["TOTAL_CHANGE"] = total_change.round(2).astype(str) + " TL (" + total_pct_change.round(2).astype(str) + "%)"

            # Add fund columns (TL + %)
            for col in df_table.columns:
                df_display[col] = df_table[col].round(2).astype(str) + " TL (" + df_pct[col].round(2).astype(str) + "%)"

            st.dataframe(df_display)

            # --- Top / Bottom Funds ---
            st.subheader("🔹 Top / Bottom Funds")
            st.markdown("**Top 5 Funds by Percentage Gain:**")
            top5_pct = result["top5_pct"].round(2).reset_index()
            top5_pct.columns = ["Fund Code", "% Change"]
            st.table(top5_pct)

            st.markdown("**Top 5 Funds by TL Gain:**")
            top5_tl = result["top5_tl"].round(2).reset_index()
            top5_tl.columns = ["Fund Code", "TL Change"]
            st.table(top5_tl)

            st.markdown("**Bottom 5 Funds by Percentage Loss:**")
            bottom5_pct = result["fund_total_change_pct"].sort_values().head(5).round(2).reset_index()
            bottom5_pct.columns = ["Fund Code", "% Change"]
            st.table(bottom5_pct)

            st.markdown("**Bottom 5 Funds by TL Loss:**")
            bottom5_tl = result["fund_total_change_tl"].sort_values().head(5).round(2).reset_index()
            bottom5_tl.columns = ["Fund Code", "TL Change"]
            st.table(bottom5_tl)

            # --- General Summary ---
            st.subheader("🔹 Summary (Selected Date Range)")
            st.markdown(f"- Start Date: {start_date}")
            st.markdown(f"- End Date: {end_date}")
            st.markdown(f"- Total Portfolio Start Value: {result['pivot'].iloc[0].sum():.2f} TL")
            st.markdown(f"- Total Portfolio End Value: {result['pivot'].iloc[-1].sum():.2f} TL")
            st.markdown(f"- Total Portfolio Change: {(result['pivot'].iloc[-1].sum() - result['pivot'].iloc[0].sum()):.2f} TL ({((result['pivot'].iloc[-1].sum() - result['pivot'].iloc[0].sum()) / result['pivot'].iloc[0].sum() * 100):.2f}%)")

            # --- Daily Total Table (Funds + Other Assets) ---
            st.subheader("🔹 Daily Total Values (Funds + Other Assets)")
            dates = result["pivot"].index
            df_assets = pd.DataFrame(index=dates, columns=["Precious Metals", "Crypto", "Physical Gold"])

            for date in dates:
                file_path = f"data_assets/{date}.txt"
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        line = f.readline().strip()
                        values = line.split("\t")
                        df_assets.loc[date] = [float(v) for v in values]
                else:
                    df_assets.loc[date] = [0.0, 0.0, 0.0]

            daily_fund_total = result["pivot"].sum(axis=1)

            df_daily = pd.DataFrame({
                "Fund Total (TL)": daily_fund_total,
                "Precious Metals (TL)": df_assets["Precious Metals"],
                "Crypto (TL)": df_assets["Crypto"],
                "Physical Gold (TL)": df_assets["Physical Gold"]
            })
            df_daily["TOTAL (TL)"] = df_daily.sum(axis=1)
            st.dataframe(df_daily.round(2))
