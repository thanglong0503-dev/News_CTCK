import math
import streamlit as st
import pandas as pd
from backend.official_news import fetch_mainstream_news
from datetime import datetime

def render_news_section():
    # 1. KÉO DỮ LIỆU
    df_news = fetch_mainstream_news()
    
    # 2. KHỞI TẠO BỘ NHỚ (SESSION STATE) CHO PHÂN TRANG & TÌM KIẾM
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""

    # 3. GIAO DIỆN TÌM KIẾM & LỌC (Khối xám)
    st.markdown("<div class='section-title' style='margin-top: 0px;'>Tra cứu Thông tin</div>", unsafe_allow_html=True)
    
    # Tạo box nền xám bao quanh thanh tìm kiếm
    with st.container():
        st.markdown("<div style='background-color: #F0F2F5; padding: 20px; border-radius: 8px; margin-bottom: 24px; border: 1px solid #E5E7EB;'>", unsafe_allow_html=True)
        
        # Hàng 1: Ô Search và Nút tìm kiếm
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            search_val = st.text_input("Tìm kiếm", value=st.session_state.search_query, placeholder="Gõ mã CK hoặc Tên công ty...", label_visibility="collapsed")
        with col_btn:
            if st.button("🔍 Tìm kiếm", use_container_width=True):
                st.session_state.search_query = search_val
                st.session_state.current_page = 1 # Reset về trang 1 khi search mới
                
        # Hàng 2: Radio Phân loại & Dropdown Thời gian
        col_radio, col_time = st.columns([4, 2])
        with col_radio:
            filter_type = st.radio("Phân loại:", ["Tất cả", "Công ty", "Tin tức", "Lãnh đạo", "Cổ phiếu quan tâm"], horizontal=True, label_visibility="collapsed")
        with col_time:
            time_filter = st.selectbox("Thời gian:", ["Mọi lúc", "Hôm nay", "Tuần này"], label_visibility="collapsed")
            
        st.markdown("</div>", unsafe_allow_html=True)

    # Nếu không có dữ liệu, báo lỗi và dừng
    if df_news.empty:
        st.info("Đang cập nhật tin tức thị trường. Vui lòng quay lại sau.")
        return

    # 4. LOGIC XỬ LÝ DỮ LIỆU (LỌC & TÌM KIẾM)
    filtered_df = df_news.copy()
    
    # Lọc theo Từ khóa tìm kiếm
    if st.session_state.search_query:
        query = st.session_state.search_query.lower()
        # Tìm trong cột title hoặc tag
        filtered_df = filtered_df[filtered_df['title'].str.lower().str.contains(query) | filtered_df['tag'].str.lower().str.contains(query)]
        
    # Lọc theo Tùy chọn Radio
    if filter_type == "Tin tức":
        filtered_df = filtered_df[filtered_df['tag'] == "Tin vĩ mô"]
    elif filter_type == "Cổ phiếu quan tâm":
        filtered_df = filtered_df[filtered_df['tag'] == "🔥 Cổ phiếu quan tâm"]
    # (Tương lai có thể map "Công ty" và "Lãnh đạo" khi AI phân tích sâu hơn)

    # Lọc theo Thời gian (Vì RSS lấy tin cực mới nên mặc định hầu hết là Hôm nay/Tuần này)
    if time_filter == "Hôm nay":
        today_str = datetime.now().strftime("%d/%m/%Y")
        filtered_df = filtered_df[filtered_df['date'].str.contains(today_str)]

    # 5. LOGIC PHÂN TRANG (PAGINATION)
    ITEMS_PER_PAGE = 8 # Hiển thị 8 tin 1 trang (vừa đẹp lưới 2x4)
    total_items = len(filtered_df)
    total_pages = math.ceil(total_items / ITEMS_PER_PAGE) if total_items > 0 else 1
    
    # Đảm bảo trang hiện tại không vượt quá tổng số trang sau khi lọc
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = total_pages
        
    start_idx = (st.session_state.current_page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    paged_df = filtered_df.iloc[start_idx:end_idx]

    # 6. RENDER LƯỚI BÀI VIẾT CỦA TRANG HIỆN TẠI
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

    # 7. RENDER THANH PHÂN TRANG (PAGINATION CONTROLS)
    if total_pages > 1:
        st.markdown("<br><br>", unsafe_allow_html=True) # Khoảng trắng cho thoáng
        # Chia cột để ép nút phân trang ra chính giữa màn hình
        pag_cols = st.columns([3, 1, 2, 1, 3]) 
        
        with pag_cols[1]:
            if st.button("◀ Trước", disabled=(st.session_state.current_page == 1), use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()
                
        with pag_cols[2]:
            st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: 600; color: #474D57;'>Trang {st.session_state.current_page} / {total_pages}</div>", unsafe_allow_html=True)
            
        with pag_cols[3]:
            if st.button("Sau ▶", disabled=(st.session_state.current_page == total_pages), use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()
