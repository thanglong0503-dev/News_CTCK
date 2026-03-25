import streamlit as st

def render_header():
    st.markdown("<h1 style='font-size: 32px; color: #1E2329; font-weight: 700; margin-bottom: 8px;'>Vietnam Securities Research</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #474D57; font-size: 16px; margin-bottom: 40px;'>Cung cấp phân tích cấp tổ chức, thông tin chuyên sâu và biểu phí khách quan cho nhà đầu tư.</p>", unsafe_allow_html=True)

def render_hero_section():
    col1, col_space, col2 = st.columns([1.2, 0.1, 1]) 

    with col1:
        st.image("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop", use_container_width=True)

    with col2:
        st.markdown("<div class='category-tag'>Phân tích phí & Margin</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-title'>Cập nhật danh mục Ký quỹ: Biến động và Cơ hội tối ưu chi phí</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-desc'>Khám phá những thay đổi mới nhất về tỷ lệ cho vay margin từ các CTCK top đầu. Đánh giá tác động đến sức mua và chiến lược phòng ngừa rủi ro (hedging) trong ngắn hạn.</div>", unsafe_allow_html=True)
        st.markdown("""
            <div style='display: flex; align-items: center;'>
                <span class='hero-meta'>2026-03-25</span>
                <span class='hero-hashtag'>#MarginRate #BrokerFee</span>
            </div>
        """, unsafe_allow_html=True)
def render_search_filter():
    st.markdown("<div class='section-title'>Latest Insights (Tin tức mới nhất)</div>", unsafe_allow_html=True)
    
    # Chia cột cho thanh tìm kiếm và nút lọc
    col_filter, col_space, col_search = st.columns([2, 1, 1])
    
    with col_filter:
        # Sử dụng pills (nút dạng viên thuốc) của Streamlit để làm bộ lọc
        st.pills("Bộ lọc:", ["Tất cả", "Cập nhật Margin", "Biểu phí", "Sản phẩm mới"], default="Tất cả", label_visibility="collapsed")
        
    with col_search:
        st.text_input("Tìm kiếm", placeholder="🔍 Tìm mã cổ phiếu, CTCK...", label_visibility="collapsed")

def render_news_grid():
    # Dữ liệu giả định (Sau này sẽ lấy từ Backend/Database lên)
    mock_news = [
        {"tag": "Biểu phí", "title": "TCBS tung gói Zero Fee trọn đời cho tài khoản mở mới từ tháng 4", "date": "2026-03-24", "ctck": "TCBS"},
        {"tag": "Cập nhật Margin", "title": "SSI hạ tỷ lệ ký quỹ hàng loạt cổ phiếu Bất động sản (NVL, DXG)", "date": "2026-03-23", "ctck": "SSI"},
        {"tag": "Sản phẩm mới", "title": "VNDirect ra mắt tính năng giao dịch phái sinh siêu tốc D-Pro", "date": "2026-03-22", "ctck": "VNDirect"},
        {"tag": "Cập nhật Margin", "title": "MBS cấp lại Room Margin cho nhóm cổ phiếu ngân hàng (MBB, TCB)", "date": "2026-03-21", "ctck": "MBS"},
    ]

    # Khởi tạo lưới 2 cột
    col1, col2 = st.columns(2)
    
    # Rải dữ liệu vào 2 cột
    for i, news in enumerate(mock_news):
        # Dùng phép chia lấy dư để xếp xen kẽ: bài 0 vào cột 1, bài 1 vào cột 2...
        target_col = col1 if i % 2 == 0 else col2
        
        with target_col:
            card_html = f"""
            <div class='news-card'>
                <div class='card-tag'>{news['ctck']} • {news['tag']}</div>
                <div class='card-title'>{news['title']}</div>
                <div class='card-date'>{news['date']}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
