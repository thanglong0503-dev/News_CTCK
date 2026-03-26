import streamlit as st
from frontend.styles import apply_custom_css
# Gọi đúng 3 hàm mới nhất từ components
from frontend.components import render_header, render_hero_section, render_news_section

def render_home_page():
    apply_custom_css()
    render_header()
    render_hero_section()
    render_news_section() # Hàm mới chứa khối Xám và Phân trang
