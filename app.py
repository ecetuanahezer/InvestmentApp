import streamlit as st
import datetime
import os
import pandas as pd
from io import StringIO
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, FundValue, AssetValue
from ingest_data import parse_and_save_funds
from analyze import get_all_funds_changes

# --- Sidebar Navigation ---
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio(
    "Go to:",
    [
        "📊 Analysis",
        "➕ Add Data",
        "🗑️ Delete Data"
    ]
)

# --- PAGE 1: ANALYSIS ---
if page == "📊 Analysis":
    st.title("📊 Portfolio Analysis")

    # === Date Selection and Summary together ===
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
            else:
                result = get_all_funds_changes(start_date, end_date)
                if result is not None:
                    start_val = result["pivot"].iloc[0].sum()
                    end_val = result["pivot"].iloc[-1].sum()
                    total_change_tl = end_val - start_val
                    total_change_pct = (total_change_tl / start_val) * 100

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Start Value", f"{start_val:,.0f} TL")
                    with col2:
                        st.metric("End Value", f"{end_val:,.0f} TL")
                    st.metric("Change", f"{total_change_tl:,.0f} TL", f"{total_change_pct:.4f}%")

    # === Analysis Tables ===
    if show_btn and start_date <= end_date:
        result = get_all_funds_changes(start_date, end_date)
        if result is not None:
            st.markdown("---")

            # --- Daily Total Values ---
            st.subheader("📅 Daily Total Values (Funds + Assets)")
            dates = result["pivot"].index
            df_assets = pd.DataFrame(index=dates, columns=["Precious Metals", "Crypto", "Physical Gold"])

            for date in dates:
                file_path = f"data_assets/{date}.txt"
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        if len(lines) >= 2:
                            values = lines[1].strip().split("\t")
                        else:
                            values = ["0", "0", "0"]
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
            st.dataframe(df_daily.round(2), use_container_width=True)

            # --- Daily Fund Changes ---
            st.subheader("📈 Daily Fund Changes")
            df_table = result["fund_changes"].fillna(0)
            df_pct = result["fund_pct_changes"].fillna(0)

            daily_total = result["pivot"].sum(axis=1)
            total_change = result["total_change"].fillna(0)
            total_pct_change = result["total_pct_change"].fillna(0)

            df_display = pd.DataFrame(index=df_table.index)
            df_display["TOTAL_TL"] = daily_total.round(2)
            df_display["TOTAL_CHANGE"] = total_change.round(2).astype(str) + " TL (" + total_pct_change.round(2).astype(str) + "%)"

            for col in df_table.columns:
                df_display[col] = df_table[col].round(2).astype(str) + " TL (" + df_pct[col].round(2).astype(str) + "%)"

            st.dataframe(df_display, use_container_width=True)

            # --- Top / Bottom 5 ---
            st.subheader("🏆 Top / Bottom Funds (Overall Period)")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Top 5 by % Gain:**")
                top5_pct = result["top5_pct"].round(2).reset_index()
                top5_pct.columns = ["Fund Code", "% Change"]
                st.table(top5_pct)

                st.markdown("**Top 5 by TL Gain:**")
                top5_tl = result["top5_tl"].round(2).reset_index()
                top5_tl.columns = ["Fund Code", "TL Change"]
                st.table(top5_tl)

            with col2:
                st.markdown("**Bottom 5 by % Loss:**")
                bottom5_pct = result["fund_total_change_pct"].sort_values().head(5).round(2).reset_index()
                bottom5_pct.columns = ["Fund Code", "% Change"]
                st.table(bottom5_pct)

                st.markdown("**Bottom 5 by TL Loss:**")
                bottom5_tl = result["fund_total_change_tl"].sort_values().head(5).round(2).reset_index()
                bottom5_tl.columns = ["Fund Code", "TL Change"]
                st.table(bottom5_tl)
                
# --- PAGE 2: ADD DATA ---
elif page == "➕ Add Data":
    st.header("📥 Add Fund Data")
    upload_date_fund = st.date_input("Select fund data date:", datetime.date.today(), key="fund_date")

    uploaded_file = st.file_uploader("Upload a text file (.txt)", type=["txt"], key="fund_file")
    text_input = st.text_area("Or paste the data here (funds and values, tab-separated, 2 lines):", key="fund_text")

    if st.button("Add Fund Data"):
        if uploaded_file is not None:
            content_bytes = uploaded_file.getvalue()
            content_str = content_bytes.decode("utf-8")
            parse_and_save_funds(StringIO(content_str), upload_date_fund)
            os.makedirs("data", exist_ok=True)
            with open(f"data/{upload_date_fund}.txt", "wb") as f:
                f.write(content_bytes)
            st.success(f"✅ Fund data for {upload_date_fund} uploaded and saved.")
        elif text_input.strip() != "":
            parse_and_save_funds(StringIO(text_input), upload_date_fund)
            os.makedirs("data", exist_ok=True)
            with open(f"data/{upload_date_fund}.txt", "w", encoding="utf-8") as f:
                f.write(text_input)
            st.success(f"✅ Fund data for {upload_date_fund} uploaded and saved.")
        else:
            st.warning("⚠️ Please upload a file or paste the data.")

    st.markdown("---")
    st.header("💰 Add Other Assets")
    upload_date_assets = st.date_input("Select other assets date:", datetime.date.today(), key="asset_date")
    metal = st.number_input("Precious Metals (TL)", min_value=0.0, step=1.0)
    crypto = st.number_input("Crypto (TL)", min_value=0.0, step=1.0)
    physical_gold = st.number_input("Physical Gold (TL)", min_value=0.0, step=1.0)

    if st.button("Add Other Assets"):
        os.makedirs("data_assets", exist_ok=True)
        with open(f"data_assets/{upload_date_assets}.txt", "w", encoding="utf-8") as f:
            f.write("Precious Metals\tCrypto\tPhysical Gold\n")
            f.write(f"{metal}\t{crypto}\t{physical_gold}")
        st.success(f"✅ Other assets for {upload_date_assets} saved successfully.")

# --- PAGE 3: DELETE DATA ---
elif page == "🗑️ Delete Data":
    st.title("🗑️ Delete Data")

    delete_date = st.date_input("Select a date to delete data", datetime.date.today())
    # --- Two columns for buttons ---
    col1, col2 = st.columns(2)
    # --- Delete Fund Data ---
    with col1:
        st.subheader("💼 Delete Fund Data")
        if st.button("Delete Fund Data"):
            session = SessionLocal()
            existing_funds = session.query(FundValue).filter(FundValue.date == delete_date).count()
            if existing_funds == 0:
                st.warning(f"⚠️ No fund data found for {delete_date}.")
            else:
                deleted_rows = session.query(FundValue).filter(FundValue.date == delete_date).delete()
                session.commit()
                st.success(f"✅ Deleted {deleted_rows} fund records for {delete_date}.")
            session.close()

            fund_file_path = os.path.join("data", f"{delete_date}.txt")
            if os.path.exists(fund_file_path):
                os.remove(fund_file_path)
                st.info(f"🗂️ File 'data/{delete_date}.txt' was also removed.")
            elif existing_funds == 0:
                st.info("No corresponding fund file found.")

    # --- Delete Asset Data ---
    with col2:
        st.subheader("🏦 Delete Asset Data")
        if st.button("Delete Asset Data"):
            session = SessionLocal()
            existing_assets = session.query(AssetValue).filter(AssetValue.date == delete_date).count()
            if existing_assets == 0:
                st.warning(f"⚠️ No asset data found for {delete_date}.")
            else:
                deleted_rows = session.query(AssetValue).filter(AssetValue.date == delete_date).delete()
                session.commit()
                st.success(f"✅ Deleted {deleted_rows} asset records for {delete_date}.")
            session.close()

            asset_file_path = os.path.join("data_assets", f"{delete_date}.txt")
            if os.path.exists(asset_file_path):
                os.remove(asset_file_path)
                st.info(f"🗂️ File 'data_assets/{delete_date}.txt' was also removed.")
            elif existing_assets == 0:
                st.info("No corresponding asset file found.")
