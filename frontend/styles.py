import streamlit as st

def apply_custom_css():
    custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Áp dụng font chữ toàn hệ thống */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            color: #1E2329;
        }

        /* Ẩn Header/Footer mặc định của Streamlit */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Chỉnh màu nền chính */
        .stApp { background-color: #FAFAFA; }

        /* Định dạng các component UI */
        .category-tag { background-color: #F5F5F5; color: #474D57; padding: 4px 12px; border-radius: 4px; font-size: 14px; font-weight: 500; display: inline-block; margin-bottom: 16px; }
        .hero-title { font-size: 40px; font-weight: 700; line-height: 1.2; color: #1E2329; margin-bottom: 16px; }
        .hero-desc { font-size: 16px; color: #474D57; line-height: 1.5; margin-bottom: 24px; }
        .hero-meta { font-size: 14px; color: #1E2329; font-weight: 600; }
        .hero-hashtag { font-size: 14px; color: #474D57; font-weight: 400; margin-left: 12px; }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
/* ... (giữ nguyên phần CSS cũ ở trên) ... */

        /* CSS cho thanh tiêu đề danh sách */
        .section-title { font-size: 24px; font-weight: 700; color: #1E2329; margin-top: 48px; margin-bottom: 24px; }

        /* CSS cho các thẻ bài viết (Cards) */
        .news-card {
            background-color: #FFFFFF;
            border: 1px solid #EAECEF;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.2s ease-in-out;
            cursor: pointer;
            height: 100%;
        }
        .news-card:hover {
            border-color: #FCD535; /* Màu vàng Binance khi hover */
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transform: translateY(-2px);
        }
        .card-tag { font-size: 12px; font-weight: 500; color: #848E9C; text-transform: uppercase; margin-bottom: 12px; }
        .card-title { font-size: 18px; font-weight: 600; color: #1E2329; margin-bottom: 12px; line-height: 1.4; }
        .card-date { font-size: 14px; color: #848E9C; }
