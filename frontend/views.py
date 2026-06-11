import streamlit as st
from frontend.styles import apply_custom_css
# Phải import đủ 5 hàm này nhé
from frontend.components import render_topbar_clock, render_header, render_hero_section, render_news_section, render_footer

def render_home_page():
    apply_custom_css()
    
    # Thứ tự xếp gạch xây web:
    render_topbar_clock() # 1. Đồng hồ màu Cam trên cùng
    render_header()       # 2. Tiêu đề
    render_hero_section() # 3. Tổng quan 4 cột & Tin nóng
    render_news_section() # 4. Lưới tin tức
    render_footer()       # 5. Footer bản quyền (ThangLong)

    # ==========================================
    # BONG BÓNG CHAT
    URL_APP_CHAT = "https://jtkbj9wk5udrrxvrrwpr8j.streamlit.app"
    # TRUYỀN THẲNG CHỮ VÀO ĐÂY, CSS SẼ LO VIỆC BIẾN NÓ THÀNH VIÊN THUỐC
    with st.popover("💬 LINANCE AI BOT", use_container_width=False):
        st.components.v1.iframe(f"{URL_APP_CHAT}/?embed=true", width=380, height=550)
