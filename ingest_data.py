"""
Contains functions to parse the raw data file and save it to the database.
"""
import datetime
import glob
import os
from sqlalchemy.exc import IntegrityError
from database import FundValue, SessionLocal, init_db


def parse_and_save(file_path_or_buffer, date: datetime.date):
    """
    Saves fund data from a text file or StringIO to the database.
    file_path_or_buffer: str or StringIO - path to the text file or StringIO object
    date: datetime.date - the date for the fund values
    """
    # Dosya yolu veya file-like object kontrolü
    if isinstance(file_path_or_buffer, str):
        f = open(file_path_or_buffer, "r", encoding="utf-8")
    else:  # StringIO veya benzeri file-like object
        f = file_path_or_buffer

    with f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    if len(lines) < 2:
        print(f"{file_path_or_buffer} wrong format: there are less than 2 lines.")
        return

    names = lines[0].split("\t")
    values = lines[1].split("\t")

    if len(names) != len(values):
        print(f"{file_path_or_buffer} wrong format: {len(names)} fund name, {len(values)} values found.")
        return

    # Değerleri float'a çevir
    try:
        values = [float(v.replace(",", ".")) for v in values]
    except ValueError:
        print(f"{file_path_or_buffer} error: could not convert all values to float.")
        return

    # DB bağlantısı
    session = SessionLocal()

    added_count = 0
    for name, value in zip(names, values):
        code = name.split()[0]  # Eg: GTZ-GPY
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
            print(f"⚠️ Skip duplicate data: {code} ({date})")

    session.close()
    print(f"From {file_path_or_buffer} file {added_count} number of funds added.")


def load_all_data():
    """ Loads and saves all fund data files from the 'data/' folder."""
    init_db()
    files = sorted(glob.glob("data/*.txt"))

    if not files:
        print("'data/' no data files found. Please add data files in 'data/' folder.")
        return

    for file_path in files:
        filename = os.path.basename(file_path)
        try:
            date_str = filename.replace(".txt", "")
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"{filename} wrong filename format. Use YYYY-MM-DD.txt")
            continue

        parse_and_save(file_path, date)


if __name__ == "__main__":
    load_all_data()
