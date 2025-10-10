# 💸 Investment Funds Tracker App

A simple **Streamlit** web app to track and analyze investment fund performance over time.  
The app allows you to:
- Upload daily fund values (from a text file or text input)
- Add other assets such as **precious metals**, **crypto**, and **physical gold**
- Delete fund/asset data if needed
- View daily fund-level changes (TL and %)
- Analyze total portfolio performance between selected dates
- Identify top and bottom performing funds

---

## 🚀 Features

✅ Upload and store daily fund data  
✅ Record other asset types manually  
✅ Automatically calculate daily and total portfolio changes  
✅ Display top/bottom 5 funds by TL and % gain  
✅ View combined daily portfolio table (funds + other assets)  

---

## 🧩 Project Structure

investmentapp

* app.py # Streamlit app (main interface)
* analyze.py # Fund change calculations
* ingest_data.py # Data parsing and ingestion
* database.py # SQLAlchemy database setup

* data/ # Saved fund data (daily .txt files)
* data_assets/ # Saved asset data (daily .txt files)

* requirements.txt # Python dependencies
* README.md # Project documentation

## ⚙️ Installation & Setup

### 1 Clone the repository
bash
* git clone https://github.com/ecetuanahezer/InvestmentApp.git
* cd investmentapp

### 2 Create a virtual environment (recommended)
* python -m venv venv
* source venv/bin/activate    # On macOS/Linux
* source venv/Scripts/activate       # On Windows

### 3 Install dependencies
pip install -r requirements.txt

### 4 Initial Data Load
Before running the Streamlit app for the first time, you should initialize the database and import all existing data files.
Run the following command once:
- python ingest_data.py

### ▶️ How to Run
- streamlit run app.py