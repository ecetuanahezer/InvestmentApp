import streamlit as st
import os
import calendar
import datetime
from database import SessionLocal, FundValue, AssetValue


def get_existing_months(base_dirs=("data_funds", "data_assets")):
    """Returns a sorted list of existing month folders like ['2025-09', '2025-10']"""
    months = set()
    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            continue
        for folder in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder)
            if os.path.isdir(folder_path) and "-" in folder:
                months.add(folder)
    return sorted(months)


def format_month_label(month_folder):
    """For UI: '2025-10' → 'October 2025'"""
    try:
        year, month = map(int, month_folder.split("-"))
        month_name = calendar.month_name[month]
        return f"{month_name} {year}"
    except Exception:
        return month_folder


def delete_entire_month(label, year, month, month_folder):
    """Deletes all data and files for a given month."""
    session = SessionLocal()

    start_date = datetime.date(year, month, 1)
    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime.date(year, month, end_day)

    deleted_funds = (
        session.query(FundValue)
        .filter(FundValue.date.between(start_date, end_date))
        .delete()
    )
    deleted_assets = (
        session.query(AssetValue)
        .filter(AssetValue.date.between(start_date, end_date))
        .delete()
    )
    session.commit()
    session.close()

    # Delete files and folders
    for folder in [os.path.join("data_funds", month_folder), os.path.join("data_assets", month_folder)]:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                os.remove(os.path.join(folder, f))
            os.rmdir(folder)

    st.success(
        f"✅ Deleted all data for {label} "
        f"({deleted_funds} fund rows, {deleted_assets} asset rows)."
    )


def delete_data():
    st.title("🗑️ Delete Data")

    months = get_existing_months()
    if not months:
        st.info("ℹ️ No data folders found yet.")
        return

    # Mapping: label <-> folder
    month_labels = [format_month_label(m) for m in months]
    month_map = dict(zip(month_labels, months))

    st.subheader("📅 Select a month:")

    # Display buttons in rows (3 per row)
    num_cols = 3
    rows = [month_labels[i:i + num_cols] for i in range(0, len(month_labels), num_cols)]

    # State initialization
    if "selected_month" not in st.session_state:
        st.session_state.selected_month = None
    if "delete_month_trigger" not in st.session_state:
        st.session_state.delete_month_trigger = False
    if "delete_day_trigger" not in st.session_state:
        st.session_state.delete_day_trigger = False
        
    # Month selection buttons
    for row in rows:
        cols = st.columns(len(row))
        for i, label in enumerate(row):
            month_folder = month_map[label]
            if cols[i].button(label, key=f"btn_{month_folder}"):
                st.session_state.selected_month = month_folder

    # If a month is selected, show delete options
    if st.session_state.selected_month:
        selected_month_folder = st.session_state.selected_month
        label = format_month_label(selected_month_folder)
        year, month = map(int, selected_month_folder.split("-"))

        st.markdown(f"### 🗓️ {label}")

        # Entire month delete
        if st.button(f"🗑️ Delete Entire Month Data ({label})", key=f"del_month_{selected_month_folder}"):
            st.session_state.confirm_delete_month = True

        if st.session_state.get("confirm_delete_month", False):
            st.warning(f"⚠️ Are you sure you want to delete ALL data for {label}? This action cannot be undone.")
            confirm_month = st.checkbox("Yes, I want to permanently delete this month's data.", key=f"chk_month_{selected_month_folder}")
            if confirm_month and st.button("🚨 Confirm Delete Month", key=f"confirm_btn_{selected_month_folder}"):
                delete_entire_month(label, year, month, selected_month_folder)
                st.session_state.confirm_delete_month = False
        
        # Specific day delete
        funds_month_dir = os.path.join("data_funds", selected_month_folder)
        assets_month_dir = os.path.join("data_assets", selected_month_folder)
        fund_files = sorted(os.listdir(funds_month_dir)) if os.path.exists(funds_month_dir) else []
        asset_files = sorted(os.listdir(assets_month_dir)) if os.path.exists(assets_month_dir) else []

        if fund_files or asset_files:
            available_days = sorted({f.replace(".txt", "") for f in fund_files + asset_files})
            selected_day = st.selectbox("Select a date to delete:", available_days, key=f"day_{selected_month_folder}")

            if st.button(f"🗑️ Delete {selected_day} Data", key=f"del_day_{selected_month_folder}"):
                st.session_state.confirm_delete_day = selected_day

            if st.session_state.get("confirm_delete_day") == selected_day:
                st.warning(f"⚠️ Are you sure you want to delete data for {selected_day}? This action cannot be undone.")
                confirm_day = st.checkbox("Yes, permanently delete this day’s data.", key=f"chk_day_{selected_month_folder}_{selected_day}")
                if confirm_day and st.button("🚨 Confirm Delete Day", key=f"confirm_day_btn_{selected_month_folder}_{selected_day}"):
                    date_obj = datetime.datetime.strptime(selected_day, "%Y-%m-%d").date()
                    session = SessionLocal()
                    deleted_funds = session.query(FundValue).filter(FundValue.date == date_obj).delete()
                    deleted_assets = session.query(AssetValue).filter(AssetValue.date == date_obj).delete()
                    session.commit()
                    session.close()

                    # Delete files
                    for base_dir in ["data_funds", "data_assets"]:
                        file_path = os.path.join(base_dir, selected_month_folder, f"{selected_day}.txt")
                        if os.path.exists(file_path):
                            os.remove(file_path)

                    st.success(f"✅ Deleted data for {selected_day} ({deleted_funds} fund rows, {deleted_assets} asset rows).")