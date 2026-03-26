import math
import streamlit as st
import pandas as pd
from backend.official_news import fetch_mainstream_news
from datetime import datetime

# --- KHỐI 1: HEADER & HERO (CAROUSEL THUẦN CSS - ĐẢM BẢO CHẠY 100%) ---
def render_header():
    st.markdown("<h1 style='font-size: 32px; color: #1E2329; font-weight: 700; margin-bottom: 8px;'>Vietnam Securities Research</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #474D57; font-size: 16px; margin-bottom: 40px;'>Cung cấp phân tích cấp tổ chức, thông tin chuyên sâu và biểu phí khách quan cho nhà đầu tư.</p>", unsafe_allow_html=True)

def render_hero_section():
    col_img, col_space, col_carousel = st.columns([1.2, 0.1, 1]) 
    
    with col_img:
        st.image("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop", use_container_width=True)
    
    with col_carousel:
        df_news = fetch_mainstream_news()
        st.markdown("<div class='category-tag' style='margin-bottom: 16px;'>🔥 Bản Tin Tóm Tắt Nhanh</div>", unsafe_allow_html=True)

        if df_news.empty:
            st.warning("Đang chờ cập nhật tin nóng...")
            return

        # Lọc lấy 5 tin nóng nhất
        hot_news_df = df_news[df_news['tag'].str.contains('🔥')].head(5)
        if hot_news_df.empty:
            hot_news_df = df_news.head(5)

        # 1. CSS TẠO THANH CUỘN NGANG (Không dùng JS)
        css = """
        <style>
        .scroll-container {
            display: flex;
            overflow-x: auto;
            scroll-snap-type: x mandatory;
            gap: 16px;
            padding-bottom: 12px;
            scroll-behavior: smooth;
        }
        /* Làm đẹp thanh cuộn */
        .scroll-container::-webkit-scrollbar { height: 6px; }
        .scroll-container::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
        .scroll-container::-webkit-scrollbar-thumb { background: #ccc; border-radius: 4px; }
        .scroll-container::-webkit-scrollbar-thumb:hover { background: #F6465D; }
        
        /* Thiết kế thẻ bài viết */
        .scroll-card {
            scroll-snap-align: start;
            min-width: 100%; /* Mỗi thẻ chiếm 100% chiều ngang */
            background: #fff;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 24px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: center;
            transition: all 0.3s ease;
        }
        .scroll-card:hover { border-color: #F6465D; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        </style>
        """

        # 2. RÁP NỘI DUNG VÀO THẺ
        cards_html = ""
        for i, row in hot_news_df.iterrows():
            summary = ' '.join(row['title'].split()[:25]) + "..."
            cards_html += f"""
            <a href="{row['link']}" target="_blank" class="scroll-card" style="text-decoration: none; color: inherit;">
                <div style="color: #707A8A; font-size: 12px; margin-bottom: 12px; font-weight: 600; text-transform: uppercase;">
                    {row['ctck']} • {row['date']}
                </div>
                <div style="color: #1E2329; font-size: 20px; font-weight: 700; line-height: 1.4; margin-bottom: 12px;">
                    {row['title']}
                </div>
                <div style="color: #474D57; font-size: 15px; line-height: 1.6;">
                    {summary}
                </div>
            </a>
            """

        # 3. HIỂN THỊ LÊN GIAO DIỆN
        html_block = f"{css}<div class='scroll-container'>{cards_html}</div>"
        st.markdown(html_block, unsafe_allow_html=True)

# --- KHỐI 2: TÌM KIẾM, LỌC & LƯỚI BÀI VIẾT (Giữ nguyên) ---
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
