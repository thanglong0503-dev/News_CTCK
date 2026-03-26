import math
import streamlit as st
import pandas as pd
from backend.official_news import fetch_mainstream_news
from backend.market_data import fetch_realtime_data # Nhúng hàm lấy giá vừa tạo
from datetime import datetime

# --- KHỐI 1: HEADER ---
def render_header():
    st.markdown("<h1 style='font-size: 32px; color: #1E2329; font-weight: 700; margin-bottom: 8px;'>Vietnam Securities Research</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #474D57; font-size: 16px; margin-bottom: 32px;'>Cung cấp phân tích cấp tổ chức, thông tin chuyên sâu và biểu phí khách quan cho nhà đầu tư.</p>", unsafe_allow_html=True)

# --- KHỐI 2: TỔNG QUAN THỊ TRƯỜNG (UI BINANCE) & TIN NÓNG ---
def render_hero_section():
    # 2.1 BAR MENU ĐIỀU HƯỚNG TỔNG QUAN
    st.markdown("""
        <div style="display: flex; gap: 24px; margin-bottom: 16px; align-items: baseline;">
            <h2 style='font-size: 22px; font-weight: 700; color: #1E2329; margin: 0;'>Tổng quan</h2>
            <span style='font-size: 16px; font-weight: 600; color: #848E9C; cursor: pointer;'>Dữ liệu Giao dịch</span>
            <span style='font-size: 16px; font-weight: 600; color: #848E9C; cursor: pointer;'>Lựa chọn của AI</span>
        </div>
    """, unsafe_allow_html=True)

    # Lấy dữ liệu Real-time
    market_data, groups = fetch_realtime_data()

    # Tạo 4 cột ngang nhau
    cols = st.columns(4)
    
    # CSS CHUẨN UI BINANCE (Đẩy sát lề trái chống lỗi Markdown)
    css_binance = """<style>
.b-card { background: #fff; border: 1px solid #EAECEF; border-radius: 12px; padding: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.01); transition: box-shadow 0.2s; }
.b-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.b-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.b-title { font-weight: 600; font-size: 14px; color: #1E2329; }
.b-more { font-size: 12px; color: #707A8A; text-decoration: none; }
.b-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.b-row:last-child { margin-bottom: 0; }
.b-left { display: flex; align-items: center; gap: 8px; width: 40%; }
.b-icon { font-size: 20px; }
.b-name { font-weight: 600; font-size: 14px; color: #1E2329; }
.b-price { font-size: 14px; color: #1E2329; text-align: left; width: 35%; font-family: monospace; font-weight: 500;}
.b-change { font-size: 14px; font-weight: 600; text-align: right; width: 25%; }
.c-up { color: #0ECB81; } /* Xanh lá chuẩn Binance */
.c-down { color: #F6465D; } /* Đỏ chuẩn Binance */
</style>"""

    # In 4 thẻ dữ liệu ra màn hình
    for col, (group_name, tickers) in zip(cols, groups.items()):
        with col:
            rows_html = ""
            for t in tickers:
                data = market_data.get(t, {"name": t, "icon": "➖", "price": "N/A", "change": 0})
                color_class = "c-up" if data['change'] >= 0 else "c-down"
                sign = "+" if data['change'] > 0 else ""
                change_str = f"{sign}{data['change']:.2f}%" if data['price'] != "N/A" else "N/A"

                rows_html += f"""<div class="b-row">
<div class="b-left"><span class="b-icon">{data['icon']}</span><span class="b-name">{data['name']}</span></div>
<div class="b-price">{data['price']}</div>
<div class="b-change {color_class}">{change_str}</div>
</div>"""

            card_html = f"""<div class="b-card">
<div class="b-header"><div class="b-title">{group_name}</div><a href="#" class="b-more">Nhiều hơn ></a></div>
{rows_html}
</div>"""
            st.markdown(f"{css_binance}{card_html}", unsafe_allow_html=True)

    # 2.2 VÒNG QUAY TIN TỨC ĐẶT NGAY BÊN DƯỚI (Full width)
    st.markdown("<br><div class='category-tag' style='margin-bottom: 16px;'>🔥 Tin Nổi Bật Giao Dịch</div>", unsafe_allow_html=True)
    df_news = fetch_mainstream_news()
    if not df_news.empty:
        hot_news_df = df_news[df_news['tag'].str.contains('🔥')].head(6)
        if hot_news_df.empty: hot_news_df = df_news.head(6)
        
        css_car = """<style>
.scroll-container { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 16px; padding-bottom: 8px; scroll-behavior: smooth; }
.scroll-container::-webkit-scrollbar { height: 4px; }
.scroll-container::-webkit-scrollbar-track { background: transparent; border-radius: 4px; }
.scroll-container::-webkit-scrollbar-thumb { background: #E5E7EB; border-radius: 4px; }
.scroll-card { scroll-snap-align: start; min-width: calc(33.333% - 11px); background: #fff; border: 1px solid #E5E7EB; border-radius: 8px; padding: 24px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; height: 180px; transition: all 0.2s ease; }
.scroll-card:hover { border-color: #F6465D; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
</style>"""

        cards_html = ""
        for i, row in hot_news_df.iterrows():
            summary = ' '.join(row['title'].split()[:18]) + "..."
            cards_html += f"""<a href="{row['link']}" target="_blank" class="scroll-card" style="text-decoration: none; color: inherit;">
<div>
<div style="color: #707A8A; font-size: 11px; margin-bottom: 8px; font-weight: 600; text-transform: uppercase;">{row['ctck']} • {row['date']}</div>
<div style="color: #1E2329; font-size: 16px; font-weight: 700; line-height: 1.35;">{summary}</div>
</div>
</a>"""
        st.markdown(f"{css_car}<div class='scroll-container'>{cards_html}</div>", unsafe_allow_html=True)


# --- KHỐI 3: TÌM KIẾM & LƯỚI TIN TỨC ---
def render_news_section():
    df_news = fetch_mainstream_news()
    
    if 'current_page' not in st.session_state: st.session_state.current_page = 1
    if 'search_query' not in st.session_state: st.session_state.search_query = ""

    st.markdown("<br><div class='section-title' style='margin-top: 0px;'>Tra cứu Thông tin Phân Tích</div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div style='background-color: #F0F2F5; padding: 20px; border-radius: 8px; margin-bottom: 24px; border: 1px solid #E5E7EB;'>", unsafe_allow_html=True)
        col_input, col_btn = st.columns([5, 1])
        with col_input: search_val = st.text_input("Tìm kiếm", value=st.session_state.search_query, placeholder="Gõ mã CK hoặc Tên công ty...", label_visibility="collapsed")
        with col_btn:
            if st.button("🔍 Tìm kiếm", use_container_width=True):
                st.session_state.search_query = search_val
                st.session_state.current_page = 1
                
        col_radio, col_time = st.columns([4, 2])
        with col_radio: filter_type = st.radio("Phân loại:", ["Tất cả", "Công ty", "Tin tức", "Lãnh đạo", "Cổ phiếu quan tâm"], horizontal=True, label_visibility="collapsed")
        with col_time: time_filter = st.selectbox("Thời gian:", ["Mọi lúc", "Hôm nay", "Tuần này"], label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    if df_news.empty: return

    filtered_df = df_news.copy()
    if st.session_state.search_query:
        query = st.session_state.search_query.lower()
        filtered_df = filtered_df[filtered_df['title'].str.lower().str.contains(query) | filtered_df['tag'].str.lower().str.contains(query)]
        
    if filter_type == "Tin tức": filtered_df = filtered_df[filtered_df['tag'] == "Tin vĩ mô"]
    elif filter_type == "Cổ phiếu quan tâm": filtered_df = filtered_df[filtered_df['tag'] == "🔥 Cổ phiếu quan tâm"]

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
                card_html = f"""<a href="{row['link']}" target="_blank" style="text-decoration: none; color: inherit;">
<div class='news-card'>
<div class='card-tag'>{row['ctck']} • {row['tag']}</div>
<div class='card-title'>{row['title']}</div>
<div class='card-date'>{row['date']}</div>
</div></a>"""
                st.markdown(card_html, unsafe_allow_html=True)

    if total_pages > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        pag_cols = st.columns([3, 1, 2, 1, 3]) 
        with pag_cols[1]:
            if st.button("◀ Trước", disabled=(st.session_state.current_page <= 1), use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()
        with pag_cols[2]: st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: 600; color: #474D57;'>Trang {st.session_state.current_page} / {total_pages}</div>", unsafe_allow_html=True)
        with pag_cols[3]:
            if st.button("Sau ▶", disabled=(st.session_state.current_page >= total_pages), use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()
