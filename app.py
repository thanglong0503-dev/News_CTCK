import streamlit as st
from frontend.views import render_home_page

# Cấu hình trang (Phải đặt ở đầu file)
st.set_page_config(
    page_title="News CTCK | Research",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Chạy trang chủ
if __name__ == "__main__":
    render_home_page()
