import math
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components # Import thư viện nhúng HTML
from backend.official_news import fetch_mainstream_news
from datetime import datetime

# --- KHỐI 1: HEADER & HERO ---
def render_header():
    st.markdown("<h1 style='font-size: 32px; color: #1E2329; font-weight: 700; margin-bottom: 8px;'>Vietnam Securities Research</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #474D57; font-size: 16px; margin-bottom: 40px;'>Cung cấp phân tích cấp tổ chức, thông tin chuyên sâu và biểu phí khách quan cho nhà đầu tư.</p>", unsafe_allow_html=True)

def render_hero_section():
    # Chia cột: Cột 1 cho ảnh, Cột 2 cho Carousel tin Hot
    col_img, col_space, col_carousel = st.columns([1.2, 0.1, 1]) 
    
    with col_img:
        st.image("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop", use_container_width=True)
    
    with col_carousel:
        # 1. LẤY DỮ LIỆU TIN HOT
        df_news = fetch_mainstream_news()
        
        # Tiêu đề khối
        st.markdown("<div class='category-tag' style='margin-bottom: 16px;'>🔥 Bản Tin Tóm Tắt Nhanh</div>", unsafe_allow_html=True)

        if df_news.empty:
            st.warning("Đang chờ cập nhật tin nóng...")
            return

        # Lọc lấy 5 tin thuộc diện "🔥 Cổ phiếu quan tâm" hoặc tin mới nhất
        hot_news_df = df_news[df_news['tag'].str.contains('🔥')].head(5)
        if hot_news_df.empty:
            hot_news_df = df_news.head(3) # Nếu không có tin tag lửa, lấy 3 tin mới nhất

        # 2. TẠO CẤU TRÚC HTML CHO SLIDER (Dùng thư viện Swiper.js)
        # Tạo các slide động từ dữ liệu
        slides_html = ""
        for i, row in hot_news_df.iterrows():
            # Tóm tắt ngắn (lấy 20 từ đầu của tiêu đề)
            summary = ' '.join(row['title'].split()[:20]) + "..."
            
            slides_html += f"""
            <div class="swiper-slide">
                <a href="{row['link']}" target="_blank" style="text-decoration: none; color: inherit;">
                    <div class="slide-content">
                        <div class="slide-source">{row['ctck']} • {row['date']}</div>
                        <div class="slide-title">{row['title']}</div>
                        <div class="slide-desc">{summary}</div>
                    </div>
                </a>
            </div>
            """

        # Toàn bộ mã HTML/CSS/JS của Carousel
        # Ta nhúng CSS và JS của Swiper.js qua CDN
        carousel_html = f"""
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />

        <style>
            body {{ margin: 0; font-family: 'Source Sans Pro', sans-serif; overflow: hidden; }}
            .swiper {{ width: 100%; height: 320px; border-radius: 8px; border: 1px solid #E5E7EB; background: #fff; }}
            .swiper-slide {{ display: flex; flex-direction: column; justify-content: center; padding: 24px; box-sizing: border-box; }}
            
            .slide-content {{ cursor: pointer; }}
            .slide-source {{ color: #707A8A; font-size: 12px; margin-bottom: 8px; text-transform: uppercase; }}
            .slide-title {{ color: #1E2329; font-size: 22px; font-weight: 700; line-height: 1.3; margin-bottom: 12px; }}
            .slide-desc {{ color: #474D57; font-size: 14px; line-height: 1.5; }}
            
            /* Tùy chỉnh màu các nút phân trang */
            .swiper-pagination-bullet-active {{ background: #F6465D !important; }}
        </style>

        <div class="swiper mySwiper">
            <div class="swiper-wrapper">
                {slides_html}
            </div>
            <div class="swiper-pagination"></div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>

        <script>
            var swiper = new Swiper(".mySwiper", {{
                grabCursor: true, // Hiện bàn tay khi hover
                loop: true,       // Vòng lặp vô tận
                autoplay: {{      // Tự động chuyển slide
                    delay: 5000,
                    disableOnInteraction: false,
                }},
                pagination: {{
                    el: ".swiper-pagination",
                    clickable: true,
                }},
                // Cấu hình cho phép kéo trên PC và vuốt trên Mobile
                simulateTouch: true,
                touchRatio: 1,
                touchAngle: 45,
            }});
        </script>
        """

        # 3. NHỨNG HTML VÀO STREAMLIT
        # Chiều cao 340px để chứa Swiper (320px) và khoảng trống margin
        components.html(carousel_html, height=340)



# --- KHỐI 2: TÌM KIẾM, LỌC & LƯỚI BÀI VIẾT (Giao diện mới) ---
def render_news_section():
    df_news = fetch_mainstream_news()
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""

    st.markdown("<div class='section-title' style='margin-top: 0px;'>Tra cứu Thông tin</div>", unsafe_allow_html=True)
    
    # Hộp màu xám chứa thanh tìm kiếm
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
        st.info("Đang cập nhật tin tức thị trường. Vui lòng quay lại sau.")
        return

    # Logic lọc
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

    # Logic phân trang
    ITEMS_PER_PAGE = 8
    total_items = len(filtered_df)
    total_pages = math.ceil(total_items / ITEMS_PER_PAGE) if total_items > 0 else 1
    
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = total_pages
        
    start_idx = (st.session_state.current_page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    paged_df = filtered_df.iloc[start_idx:end_idx]

    # In bài viết
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

    # In nút Phân trang
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
