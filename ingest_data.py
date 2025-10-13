"""
Contains functions to parse and save both fund and asset data files to the database.
"""

import datetime
import glob
import os
import numpy as np
from sqlalchemy.exc import IntegrityError
from database import FundValue, AssetValue, SessionLocal, init_db


def parse_and_save_funds(file_path_or_buffer, date: datetime.date):
    """
    Saves fund data from a text file or StringIO to the database.
    file_path_or_buffer: str or StringIO - path to the text file or StringIO object
    date: datetime.date - the date for the fund values
    """
    # Detect file path or file-like object
    if isinstance(file_path_or_buffer, str):
        f = open(file_path_or_buffer, "r", encoding="utf-8")
    else:  # StringIO or similar file-like object
        f = file_path_or_buffer

    with f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    if len(lines) < 2:
        print(f"{file_path_or_buffer} wrong format: less than 2 lines found.")
        return

    names = lines[0].split("\t")
    values = lines[1].split("\t")

    if len(names) != len(values):
        print(f"{file_path_or_buffer} wrong format: {len(names)} fund names, {len(values)} values found.")
        return

    # Convert values to float
    try:
        values = [float(v.replace(",", ".")) for v in values]
    except ValueError:
        print(f"{file_path_or_buffer} error: could not convert all values to float.")
        return

    # Save to database
    session = SessionLocal()
    added_count = 0

    for name, value in zip(names, values):
        code = name.split()[0]  # Example: GTZ-GPY
        fund_name = " ".join(name.split()[1:])
        entry = FundValue(
            fund_code=code,
            fund_name=fund_name,
            value_tl=value,
            date=date,
        )
        session.add(entry)

        try:
            session.commit()
            added_count += 1
        except IntegrityError:
            session.rollback()
            print(f"⚠️ Duplicate skipped: {code} ({date})")

    session.close()
    print(f"{added_count} fund records added from {file_path_or_buffer}.")


def parse_and_save_asset(file_path_or_buffer, date: datetime.date):
    """
    Parses and saves asset data from text file or StringIO.
    Expected format:
        Line 1: Precious Metals    Crypto    Physical Gold
        Line 2: 10000    5000    2000
    """
    if isinstance(file_path_or_buffer, str):
        f = open(file_path_or_buffer, "r", encoding="utf-8")
    else:
        f = file_path_or_buffer

    with f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    if len(lines) < 2:
        print(f"{file_path_or_buffer} wrong format for asset data (less than 2 lines).")
        return

    names = [n.lower().strip() for n in lines[0].split("\t")]
    values = [v.strip() for v in lines[1].split("\t")]

    try:
        values = [float(v.replace(",", ".")) for v in values]
    except ValueError:
        print(f"{file_path_or_buffer} asset values could not be converted to float.")
        return

    session = SessionLocal()

    entry = AssetValue(
        date=date,
        precious_metals_tl=np.nan_to_num(values[0], nan=0.0),
        crypto_tl=np.nan_to_num(values[1], nan=0.0),
        physical_gold_tl=np.nan_to_num(values[2], nan=0.0),
    )

    session.add(entry)
    try:
        session.commit()
        print(f"✅ Asset data for {date} added successfully.")
    except IntegrityError:
        session.rollback()
        print(f"⚠️ Duplicate asset data for {date}, skipped.")

    session.close()
    
def load_all_data():
    """
    Loads and saves all fund and asset data files from their respective folders.
    - Fund data from 'data_funds/'
    - Asset data from 'data_assets/'
    """
    init_db()

    # --- Load fund data ---
    fund_files = sorted(glob.glob("data_funds/*.txt"))
    if not fund_files:
        print("⚠️ No fund data files found in 'data_funds/' folder.")
    else:
        for file_path in fund_files:
            filename = os.path.basename(file_path)
            try:
                date_str = filename.replace(".txt", "")
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print(f"{filename} wrong filename format. Use YYYY-MM-DD.txt")
                continue
            parse_and_save_funds(file_path, date)

    # --- Load asset data ---
    asset_files = sorted(glob.glob("data_assets/*.txt"))
    if not asset_files:
        print("⚠️ No asset data files found in 'data_assets/' folder.")
    else:
        for file_path in asset_files:
            filename = os.path.basename(file_path)
            try:
                date_str = filename.replace(".txt", "")
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print(f"{filename} wrong filename format. Use YYYY-MM-DD.txt")
                continue
            parse_and_save_asset(file_path, date)


if __name__ == "__main__":
    load_all_data()
