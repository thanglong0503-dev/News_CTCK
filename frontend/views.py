import streamlit as st
from frontend.styles import apply_custom_css
from frontend.components import render_header, render_hero_section, render_news_section

def render_home_page():
    # 1. Bơm CSS vào trang
    apply_custom_css()
    
    # 2. Lắp phần tiêu đề
    render_header()
    
    # 3. Lắp phần Hero (Ảnh & Bài viết nổi bật)
    render_hero_section()
    
    # 4. Lắp toàn bộ Khối Tìm kiếm + Lưới bài viết + Phân trang
    render_news_section()
