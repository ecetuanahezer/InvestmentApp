import streamlit as st
import datetime
import os
from io import StringIO
from ingest_data import parse_and_save_asset, parse_and_save_funds

def add_data():
    st.title("➕ Add Data")
    col1, col2 = st.columns(2)
    with col1:
        # --- Add Fund Data ---
        st.header("📥 Add Fund Data")
        upload_date_fund = st.date_input("Select fund data date:", datetime.date.today(), key="fund_date")
        uploaded_file = st.file_uploader("Upload a text file (.txt)", type=["txt"], key="fund_file")
        text_input = st.text_area("Or paste the data here (funds and values, tab-separated, 2 lines):", key="fund_text")

        if st.button("Add Fund Data"):
            if uploaded_file is not None:
                content_bytes = uploaded_file.getvalue()
                content_str = content_bytes.decode("utf-8")
                parse_and_save_funds(StringIO(content_str), upload_date_fund)
                os.makedirs("data_funds", exist_ok=True)
                with open(f"data_funds/{upload_date_fund}.txt", "wb") as f:
                    f.write(content_bytes)
                st.success(f"✅ Fund data for {upload_date_fund} uploaded and saved.")
            elif text_input.strip() != "":
                parse_and_save_funds(StringIO(text_input), upload_date_fund)
                os.makedirs("data_funds", exist_ok=True)
                with open(f"data_funds/{upload_date_fund}.txt", "w", encoding="utf-8") as f:
                    f.write(text_input)
                st.success(f"✅ Fund data for {upload_date_fund} uploaded and saved.")
            else:
                st.warning("⚠️ Please upload a file or paste the data.")
    with col2:
        # --- Add Other Assets ---
        st.header("💰 Add Other Assets")
        upload_date_assets = st.date_input("Select other assets date:", datetime.date.today(), key="asset_date")
        metal = st.number_input("Precious Metals (TL)", min_value=0.0, step=1.0)
        crypto = st.number_input("Crypto (TL)", min_value=0.0, step=1.0)
        physical_gold = st.number_input("Physical Gold (TL)", min_value=0.0, step=1.0)

        if st.button("Add Other Assets"):
            parse_and_save_asset(StringIO(f"precious_metals\tcrypto\tphysical_gold\n{metal}\t{crypto}\t{physical_gold}"), upload_date_assets)
            os.makedirs("data_assets", exist_ok=True)
            with open(f"data_assets/{upload_date_assets}.txt", "w", encoding="utf-8") as f:
                f.write("precious_metals\tcrypto\tphysical_gold\n")
                f.write(f"{metal}\t{crypto}\t{physical_gold}")
            st.success(f"✅ Other assets for {upload_date_assets} saved successfully.")
