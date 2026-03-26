import streamlit as st
from frontend.styles import apply_custom_css
# Import thêm 2 hàm mới: render_topbar_clock và render_footer
from frontend.components import render_topbar_clock, render_header, render_hero_section, render_news_section, render_footer

def render_home_page():
    apply_custom_css()
    
    # Lắp rắp theo đúng thứ tự từ trên xuống dưới
    render_topbar_clock() # 1. Dải ruy băng đồng hồ trên cùng
    render_header()       # 2. Tiêu đề Website
    render_hero_section() # 3. Khối 4 thẻ giá Binance & Vòng quay tin
    render_news_section() # 4. Khối tìm kiếm & Lưới tin tức
    render_footer()       # 5. Chữ ký bản quyền dưới cùng
