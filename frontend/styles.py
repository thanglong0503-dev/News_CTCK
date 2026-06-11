import streamlit as st

def apply_custom_css(is_dark=False):
    # Khai báo 2 bộ màu (Sáng và Tối)
    if is_dark:
        theme_vars = """
            --bg-main: #0B0E11;
            --text-main: #EAECEF;
            --text-sub: #848E9C;
            --card-bg: #181A20;
            --card-border: #2B3139;
            --tag-bg: #2B3139;
            --hover-border: #FCD535;
        """
    else:
        theme_vars = """
            --bg-main: #FAFAFA;
            --text-main: #1E2329;
            --text-sub: #474D57;
            --card-bg: #FFFFFF;
            --card-border: #EAECEF;
            --tag-bg: #F5F5F5;
            --hover-border: #FCD535;
        """

    # Do dùng f-string nên các dấu ngoặc nhọn của CSS phải viết gấp đôi {{ }}
    custom_css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Nạp bộ màu vào giao diện */
        :root {{
            {theme_vars}
        }}

        /* Áp dụng font chữ toàn hệ thống */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif !important;
            color: var(--text-main);
            transition: background-color 0.3s, color 0.3s;
        }}

        /* ĐÃ TẮT LỆNH KHÓA HEADER ĐỂ BONG BÓNG VÀ MENU KHÔNG BỊ NUỐT */
        /* header {{visibility: hidden;}} */ 
        footer {{visibility: hidden;}} /* Cứ giữ ẩn footer nếu Ngài muốn */
        
        /* Chỉnh màu nền chính */
        .stApp {{ background-color: var(--bg-main); transition: background-color 0.3s; }}

        /* Định dạng các component UI (Giữ nguyên 100% logic của Ngài) */
        .category-tag {{ background-color: var(--tag-bg); color: var(--text-sub); padding: 4px 12px; border-radius: 4px; font-size: 14px; font-weight: 500; display: inline-block; margin-bottom: 16px; transition: 0.3s; }}
        .hero-title {{ font-size: 40px; font-weight: 700; line-height: 1.2; color: var(--text-main); margin-bottom: 16px; transition: 0.3s; }}
        .hero-desc {{ font-size: 16px; color: var(--text-sub); line-height: 1.5; margin-bottom: 24px; transition: 0.3s; }}
        .hero-meta {{ font-size: 14px; color: var(--text-main); font-weight: 600; transition: 0.3s; }}
        .hero-hashtag {{ font-size: 14px; color: var(--text-sub); font-weight: 400; margin-left: 12px; transition: 0.3s; }}

        /* CSS cho thanh tiêu đề danh sách */
        .section-title {{ font-size: 24px; font-weight: 700; color: var(--text-main); margin-top: 48px; margin-bottom: 24px; transition: 0.3s; }}

        /* CSS cho các thẻ bài viết (Cards) */
        .news-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.2s ease-in-out;
            cursor: pointer;
            height: 100%;
        }}
        .news-card:hover {{
            border-color: var(--hover-border);
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transform: translateY(-2px);
        }}
        .card-tag {{ font-size: 12px; font-weight: 500; color: #848E9C; text-transform: uppercase; margin-bottom: 12px; transition: 0.3s; }}
        .card-title {{ font-size: 18px; font-weight: 600; color: var(--text-main); margin-bottom: 12px; line-height: 1.4; transition: 0.3s; }}
        .card-date {{ font-size: 14px; color: #848E9C; transition: 0.3s; }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
