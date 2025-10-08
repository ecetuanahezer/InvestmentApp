# 💸 Investment Funds Tracker App

A simple **Streamlit** web app to track and analyze investment fund performance over time.  
The app allows you to:
- Upload daily fund values (from a text file or text input)
- Add other assets such as **precious metals**, **crypto**, and **physical gold**
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


investment-funds-tracker/
│
├── app.py # Streamlit app (main interface)
├── analyze.py # Fund change calculations
├── ingest_data.py # Data parsing and ingestion
├── database.py # SQLAlchemy database setup
│
├── data/ # Saved fund data (daily .txt files)
├── data_assets/ # Saved asset data (daily .txt files)
│
├── requirements.txt # Python dependencies
└── README.md # Project documentation

## ⚙️ Installation & Setup

### 1 Clone the repository
bash
git clone https://github.com/YOUR_USERNAME/investment-funds-tracker.git
cd investment-funds-tracker

### 2 Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate    # On macOS/Linux
venv\Scripts\activate       # On Windows

### 3 Install dependencies

▶️ How to Run
streamlit run app.py