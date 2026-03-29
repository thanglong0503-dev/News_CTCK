import streamlit as st
from frontend.views import render_home_page

# Cấu hình trang (Phải đặt ở đầu file)
st.set_page_config(
    page_title="Vietnam Securities Research", # Đổi tên Tab trình duyệt
    page_icon="assets/logo.png",              # Gọi logo Linance làm icon
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chạy trang chủ
if __name__ == "__main__":
    render_home_page()
