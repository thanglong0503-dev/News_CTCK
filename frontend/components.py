import math
import streamlit as st
import pandas as pd
from backend.official_news import fetch_mainstream_news
from datetime import datetime

# --- KHỐI 1: HEADER ---
def render_header():
    st.markdown("<h1 style='font-size: 32px; color: #1E2329; font-weight: 700; margin-bottom: 8px;'>Vietnam Securities Research</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #474D57; font-size: 16px; margin-bottom: 40px;'>Cung cấp phân tích cấp tổ chức, thông tin chuyên sâu và biểu phí khách quan cho nhà đầu tư.</p>", unsafe_allow_html=True)

# --- KHỐI 2: HERO (WATCHLIST MINI & CAROUSEL) ---
def render_hero_section():
    col_watchlist, col_space, col_carousel = st.columns([1.2, 0.1, 1]) 
    
    # 2.1 BẢNG GIÁ MINI BÊN TRÁI
    with col_watchlist:
        st.markdown("<div class='category-tag' style='margin-bottom: 16px;'>Watchlist Mini: Thị Trường</div>", unsafe_allow_html=True)

        css_wl = """<style>
.watchlist-container { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 16px; padding-bottom: 8px; scroll-behavior: smooth; }
.watchlist-container::-webkit-scrollbar { height: 4px; }
.watchlist-container::-webkit-scrollbar-track { background: transparent; border-radius: 4px; }
.watchlist-container::-webkit-scrollbar-thumb { background: #E5E7EB; border-radius: 4px; }
.watchlist-card { scroll-snap-align: start; min-width: 100%; background: #fff; border: 1px solid #E5E7EB; border-radius: 8px; padding: 24px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: center; height: 320px; transition: all 0.2s ease; }
.wl-title { color: #1E2329; font-size: 16px; font-weight: 600; margin-bottom: 16px; }
.wl-table { width: 100%; border-collapse: collapse; font-family: 'Source Sans Pro', sans-serif; }
.wl-th { color: #707A8A; font-size: 12px; font-weight: 600; text-transform: uppercase; text-align: left; padding-bottom: 8px; border-bottom: 1px solid #E5E7EB; }
.wl-td-ma { color: #1E2329; font-size: 14px; font-weight: 700; padding-top: 12px; }
.wl-td-gia { color: #1E2329; font-size: 14px; padding-top: 12px; font-weight: 500; }
.wl-up { color: #0277BD; font-weight: 600; } 
.wl-down { color: #F6465D; font-weight: 600; }
</style>"""

        watchlist_html = """<div class="watchlist-card">
<div class="wl-title">Chỉ Số Vĩ Mô & Thị Trường</div>
<table class="wl-table">
<tr><th class="wl-th">Mã</th><th class="wl-th">Giá</th><th class="wl-th">+/- %</th></tr>
<tr><td class="wl-td-ma">VNINDEX</td><td class="wl-td-gia">1,250.78</td><td class="wl-td-gia wl-up">+0.35%</td></tr>
<tr><td class="wl-td-ma">USD/VND</td><td class="wl-td-gia">24,785.0</td><td class="wl-td-gia wl-up">+0.12%</td></tr>
<tr><td class="wl-td-ma">VÀNG SJC</td><td class="wl-td-gia">81.20 tr</td><td class="wl-td-gia wl-up">+0.85%</td></tr>
</table>
</div>"""

        portfolio_html = """<div class="watchlist-card">
<div class="wl-title">Cổ Phiếu Tích Sản</div>
<table class="wl-table">
<tr><th class="wl-th">Mã</th><th class="wl-th">Giá</th><th class="wl-th">+/- %</th></tr>
<tr><td class="wl-td-ma">PLX</td><td class="wl-td-gia">40.25</td><td class="wl-td-gia wl-up">+1.15%</td></tr>
<tr><td class="wl-td-ma">MBB</td><td class="wl-td-gia">21.80</td><td class="wl-td-gia wl-down">-0.45%</td></tr>
<tr><td class="wl-td-ma">TNG</td><td class="wl-td-gia">19.50</td><td class="wl-td-gia wl-up">+0.51%</td></tr>
</table>
</div>"""

        st.markdown(f"{css_wl}<div class='watchlist-container'>{watchlist_html}{portfolio_html}</div>", unsafe_allow_html=True)

    # 2.2 CAROUSEL TIN NÓNG BÊN PHẢI
    with col_carousel:
        df_news = fetch_mainstream_news()
        st.markdown("<div class='category-tag' style='margin-bottom: 16px;'>🔥 Bản Tin Tóm Tắt Nhanh</div>", unsafe_allow_html=True)

        if df_news.empty:
            st.warning("Đang chờ cập nhật tin nóng...")
            return

        hot_news_df = df_news[df_news['tag'].str.contains('🔥')].head(5)
        if hot_news_df.empty:
            hot_news_df = df_news.head(5)

        css_car = """<style>
.scroll-container { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 16px; padding-bottom: 8px; scroll-behavior: smooth; }
.scroll-container::-webkit-scrollbar { height: 4px; }
.scroll-container::-webkit-scrollbar-track { background: transparent; border-radius: 4px; }
.scroll-container::-webkit-scrollbar-thumb { background: #E5E7EB; border-radius: 4px; }
.scroll-card { scroll-snap-align: start; min-width: 100%; background: #fff; border: 1px solid #E5E7EB; border-radius: 8px; padding: 24px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; height: 320px; transition: all 0.2s ease; }
.scroll-card:hover { border-color: #F6465D; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
</style>"""

        cards_html = ""
        for i, row in hot_news_df.iterrows():
            summary = ' '.join(row['title'].split()[:22]) + "..."
            cards_html += f"""<a href="{row['link']}" target="_blank" class="scroll-card" style="text-decoration: none; color: inherit;">
<div>
<div style="color: #707A8A; font-size: 12px; margin-bottom: 12px; font-weight: 600; text-transform: uppercase;">{row['ctck']} • {row['date']}</div>
<div style="color: #1E2329; font-size: 19px; font-weight: 700; line-height: 1.35; margin-bottom: 12px;">{row['title']}</div>
</div>
<div style="color: #474D57; font-size: 14px; line-height: 1.5;">{summary}</div>
</a>"""

        st.markdown(f"{css_car}<div class='scroll-container'>{cards_html}</div>", unsafe_allow_html=True)

# --- KHỐI 3: TÌM KIẾM & LƯỚI TIN TỨC (Hàm này nãy bị mất đây) ---
def render_news_section():
    df_news = fetch_mainstream_news()
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""

    st.markdown("<br><div class='section-title' style='margin-top: 0px;'>Tra cứu Thông tin</div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div style='background-color: #F0F2F5; padding: 20px; border-radius: 8px; margin-bottom: 24px; border: 1px solid #E5E7EB;'>", unsafe_allow_html=True)
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            search_val = st.text_input("Tìm kiếm", value=st.session_state.search_query, placeholder="Gõ mã CK hoặc Tên công ty...", label_visibility="collapsed")
        with col_btn:
            if st.button("🔍 Tìm kiếm", use_container_width=True):
                st.session_state.search_query = search_val
                st.session_state.current_page = 1
                
        col_radio, col_time = st.columns([4, 2])
        with col_radio:
            filter_type = st.radio("Phân loại:", ["Tất cả", "Công ty", "Tin tức", "Lãnh đạo", "Cổ phiếu quan tâm"], horizontal=True, label_visibility="collapsed")
        with col_time:
            time_filter = st.selectbox("Thời gian:", ["Mọi lúc", "Hôm nay", "Tuần này"], label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    if df_news.empty:
        return

    filtered_df = df_news.copy()
    if st.session_state.search_query:
        query = st.session_state.search_query.lower()
        filtered_df = filtered_df[filtered_df['title'].str.lower().str.contains(query) | filtered_df['tag'].str.lower().str.contains(query)]
        
    if filter_type == "Tin tức":
        filtered_df = filtered_df[filtered_df['tag'] == "Tin vĩ mô"]
    elif filter_type == "Cổ phiếu quan tâm":
        filtered_df = filtered_df[filtered_df['tag'] == "🔥 Cổ phiếu quan tâm"]

    if time_filter == "Hôm nay":
        today_str = datetime.now().strftime("%d/%m/%Y")
        filtered_df = filtered_df[filtered_df['date'].str.contains(today_str)]

    ITEMS_PER_PAGE = 8
    total_items = len(filtered_df)
    total_pages = math.ceil(total_items / ITEMS_PER_PAGE) if total_items > 0 else 1
    
    if st.session_state.current_page > total_pages: st.session_state.current_page = total_pages
        
    start_idx = (st.session_state.current_page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    paged_df = filtered_df.iloc[start_idx:end_idx]

    if paged_df.empty:
        st.warning("Không tìm thấy kết quả nào phù hợp với từ khóa/bộ lọc của bạn.")
    else:
        col1, col2 = st.columns(2)
        for i, row in paged_df.reset_index().iterrows():
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                card_html = f"""
                <a href="{row['link']}" target="_blank" style="text-decoration: none; color: inherit;">
                    <div class='news-card'>
                        <div class='card-tag'>{row['ctck']} • {row['tag']}</div>
                        <div class='card-title'>{row['title']}</div>
                        <div class='card-date'>{row['date']}</div>
                    </div>
                </a>
                """
                st.markdown(card_html, unsafe_allow_html=True)

    if total_pages > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        pag_cols = st.columns([3, 1, 2, 1, 3]) 
        with pag_cols[1]:
            if st.button("◀ Trước", disabled=(st.session_state.current_page <= 1), use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()
        with pag_cols[2]:
            st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: 600; color: #474D57;'>Trang {st.session_state.current_page} / {total_pages}</div>", unsafe_allow_html=True)
        with pag_cols[3]:
            if st.button("Sau ▶", disabled=(st.session_state.current_page >= total_pages), use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()
