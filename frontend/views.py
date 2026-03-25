import streamlit as st
from frontend.styles import apply_custom_css
# Import thêm 2 hàm mới
from frontend.components import render_header, render_hero_section, render_search_filter, render_news_grid

def render_home_page():
    # 1. Bơm CSS vào trang
    apply_custom_css()
    
    # 2. Lắp phần tiêu đề
    render_header()
    
    # 3. Lắp phần Hero (Ảnh & Bài viết nổi bật)
    render_hero_section()
    
    # 4. Lắp thanh Search & Lọc
    render_search_filter()
    
    # 5. Lắp lưới bài viết
    st.markdown("<br>", unsafe_allow_html=True) # Tạo khoảng trắng
    render_news_grid()
