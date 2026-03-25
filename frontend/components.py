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
