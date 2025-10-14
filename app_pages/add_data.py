import streamlit as st
import datetime
import os
from io import StringIO
from ingest_data import parse_and_save_asset, parse_and_save_funds


def add_data():
    st.title("➕ Add Data")
    upload_date = st.date_input("Select data date:", datetime.date.today(), key="date")
    folder_name = upload_date.strftime("%Y-%m")  # eg: 2025-10
    display_date = upload_date.strftime("%B %d, %Y")  # eg: October 14, 2025
    col1, col2 = st.columns(2)
    with col1:
        # --- Add Fund Data ---
        st.header("📥 Add Fund Data")

        uploaded_fund_file = st.file_uploader(
            "Upload a text file (.txt)", type=["txt"], key="fund_file"
        )
        fund_text_input = st.text_area(
            "Or paste the data here (funds and values, tab-separated, 2 lines):",
            key="fund_text",
        )

    with col2:
        # --- Add Other Assets ---
        st.header("💰 Add Other Assets")

        metal = st.number_input("Precious Metals (TL)", min_value=0.0, step=1.0)
        crypto = st.number_input("Crypto (TL)", min_value=0.0, step=1.0)
        physical_gold = st.number_input("Physical Gold (TL)", min_value=0.0, step=1.0)

    if st.button("Add All Data"):
        # Is fund data provided either via file or text input?
        has_fund_data = uploaded_fund_file is not None or fund_text_input.strip() != ""

        # Are any asset values provided?
        has_asset_data = any([metal, crypto, physical_gold])

        if not has_fund_data:
            st.warning("⚠️ Please upload or paste fund data.")
        elif not has_asset_data:
            st.warning("⚠️ Please fill in all asset values.")
        else:
            fund_dir = os.path.join("data_funds", folder_name)
            asset_dir = os.path.join("data_assets", folder_name)
            os.makedirs(fund_dir, exist_ok=True)
            os.makedirs(asset_dir, exist_ok=True)
            # === Save Funds ===
            fund_file_path = os.path.join(fund_dir, f"{upload_date}.txt")
            if uploaded_fund_file is not None:
                fund_bytes = uploaded_fund_file.getvalue()
                fund_str = fund_bytes.decode("utf-8")
                parse_and_save_funds(StringIO(fund_str), upload_date)
                with open(fund_file_path, "wb") as f:
                    f.write(fund_bytes)
            else:
                parse_and_save_funds(StringIO(fund_text_input), upload_date)
                with open(fund_file_path, "w", encoding="utf-8") as f:
                    f.write(fund_text_input)

            # === Save Assets ===
            asset_file_path = os.path.join(asset_dir, f"{upload_date}.txt")
            parse_and_save_asset(
                StringIO(
                    f"precious_metals\tcrypto\tphysical_gold\n{metal}\t{crypto}\t{physical_gold}"
                ),
                upload_date,
            )
            with open(asset_file_path, "w", encoding="utf-8") as f:
                f.write("precious_metals\tcrypto\tphysical_gold\n")
                f.write(f"{metal}\t{crypto}\t{physical_gold}")

            st.success(
                f"✅ Fund and asset data for {upload_date} uploaded successfully!"
            )
