import streamlit as st

# 1. Cấu hình toàn cục (Phải gọi đầu tiên)
st.set_page_config(
    page_title="Vietnam Securities Terminal", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. CSS tùy chỉnh để giao diện tối màu (Dark Mode) trông pro hơn
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3 { color: #f0f2f6; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 3. Giao diện trang chủ
st.title("⚡ Vietnam Securities Intelligence Terminal")
st.markdown("Hệ thống tổng hợp, bóc tách và phân tích dữ liệu tự động từ các Công ty Chứng khoán.")

st.divider()

# 4. Khu vực Highlight (Tổng quan nhanh)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="CTCK Đang Theo Dõi", value="5 Hệ thống", delta="Hoạt động ổn định")
with col2:
    st.metric(label="Biến động phí dịch vụ", value="0.10% - 0.15%", delta="-0.02% so với tháng trước", delta_color="inverse")
with col3:
    st.metric(label="Tin tức cập nhật", value="24 Bản tin", delta="Mới nhất: SSI")

st.info("👈 Sử dụng thanh điều hướng bên trái để truy cập Dashboard Phân tích Margin và Tin tức chi tiết.")
