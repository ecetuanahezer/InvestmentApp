import streamlit as st
import datetime
import os
from database import SessionLocal, FundValue, AssetValue

def delete_data():
    st.title("🗑️ Delete Data")
    delete_date = st.date_input("Select a date to delete data", datetime.date.today())

    # --- Two columns for buttons ---
    col1, col2 = st.columns(2)

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
