import streamlit as st
from app_pages.analysis import show_analysis
from app_pages.add_data import add_data
from app_pages.delete_data import delete_data
from app_pages.visual_analysis import show_visual_analysis

# Sidebar navigation
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio(
    "Go to:", ["📊 Analysis", "📈 Visual Analysis", "➕ Add Data", "🗑️ Delete Data"]
)

# Show the selected page
if page == "📊 Analysis":
    show_analysis()
elif page == "📈 Visual Analysis":
    show_visual_analysis()
elif page == "➕ Add Data":
    add_data()
elif page == "🗑️ Delete Data":
    delete_data()
