import streamlit as st

def apply_custom_css(is_dark=False):
    # ==========================================
    # 1. CODE GỐC CỦA NGÀI (Giữ nguyên UI của Dashboard)
    # ==========================================
    custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Áp dụng font chữ toàn hệ thống */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            color: #1E2329;
        }

        /* Ẩn footer mặc định của Streamlit */
        footer {visibility: hidden;} 
        
        /* Chỉnh màu nền chính */
        .stApp { background-color: #FAFAFA; }

        /* Định dạng các component UI */
        .category-tag { background-color: #F5F5F5; color: #474D57; padding: 4px 12px; border-radius: 4px; font-size: 14px; font-weight: 500; display: inline-block; margin-bottom: 16px; }
        .hero-title { font-size: 40px; font-weight: 700; line-height: 1.2; color: #1E2329; margin-bottom: 16px; }
        .hero-desc { font-size: 16px; color: #474D57; line-height: 1.5; margin-bottom: 24px; }
        .hero-meta { font-size: 14px; color: #1E2329; font-weight: 600; }
        .hero-hashtag { font-size: 14px; color: #474D57; font-weight: 400; margin-left: 12px; }

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
            border-color: #FCD535;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transform: translateY(-2px);
        }
        .card-tag { font-size: 12px; font-weight: 500; color: #848E9C; text-transform: uppercase; margin-bottom: 12px; }
        .card-title { font-size: 18px; font-weight: 600; color: #1E2329; margin-bottom: 12px; line-height: 1.4; }
        .card-date { font-size: 14px; color: #848E9C; }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # ==========================================
    # 2. XỬ LÝ GHI ĐÈ DARK MODE
    # ==========================================
    if is_dark:
        dark_css = """
        <style>
            html, body, [class*="css"], .stApp { background-color: #0B0E11 !important; color: #EAECEF !important; }
            .hero-title, .section-title, .card-title, .hero-meta { color: #EAECEF !important; }
            .hero-desc, .hero-hashtag { color: #848E9C !important; }
            .news-card { background-color: #181A20 !important; border-color: #2B3139 !important; }
            .category-tag { background-color: #2B3139 !important; color: #848E9C !important; }
        </style>
        """
        st.markdown(dark_css, unsafe_allow_html=True)

    ## ==========================================
    # 3. CSS ĐỘC QUYỀN CHO NÚT "LINANCE AI BOT" (Giao diện Hình Chữ Nhật)
    # ==========================================
    chat_bubble_css = """
    <style>
        /* 1. Ghim nút xuống góc phải dưới cùng */
        div[data-testid="stPopover"] {
            position: fixed !important;
            bottom: 30px !important;
            right: 30px !important;
            z-index: 999999 !important;
        }
        
        /* 2. Ép hình dáng nút thành HÌNH CHỮ NHẬT vuông vức, chuyên nghiệp */
        div[data-testid="stPopover"] > button {
            border-radius: 8px !important; /* Bo góc cực nhẹ, tạo thành hình chữ nhật */
            background: linear-gradient(135deg, #FF9500, #FF5E3A) !important; /* Cam Gradient quyền lực */
            border: 1px solid rgba(255, 255, 255, 0.3) !important; /* Viền trắng siêu mỏng */
            padding: 12px 24px !important; /* Khoảng cách chữ đến viền, vừa vặn */
            box-shadow: 0 6px 16px rgba(255, 94, 58, 0.3) !important; /* Bóng đổ nhẹ nhàng, không lố */
            transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1) !important; /* Đổi hiệu ứng chuyển động dứt khoát hơn */
            min-width: 180px !important; /* Đảm bảo đủ rộng để chứa hết chữ */
        }
        
        /* 3. Hiệu ứng nảy lên nhẹ và đổ bóng sâu hơn khi đưa chuột vào */
        div[data-testid="stPopover"] > button:hover {
            transform: translateY(-3px) !important; /* Nảy lên dứt khoát */
            box-shadow: 0 10px 24px rgba(255, 94, 58, 0.5) !important;
        }
        
        /* 4. Định dạng chữ bên trong nút (Chuyên nghiệp, hiện đại) */
        div[data-testid="stPopover"] > button p {
            font-size: 15px !important; /* Kích thước chuẩn */
            font-weight: 700 !important; /* Đậm vừa đủ */
            letter-spacing: 0.8px !important; /* Giãn chữ ra một chút cho sang */
            color: #FFFFFF !important;
            margin: 0 !important;
            text-transform: uppercase !important; /* VIẾT HOA TẤT CẢ CHO QUYỀN LỰC */
            font-family: 'SF Mono', Consolas, monospace !important; /* Dùng font máy tính xịn xò */
        }
        
        /* 5. Tắt viền đỏ báo lỗi khi click chuột (Đặc sản của Streamlit) */
        div[data-testid="stPopover"] > button:focus {
            outline: none !important;
            color: white !important;
        }

        /* 6. Khung chat hiển thị cũng phải hình chữ nhật cho đồng bộ */
        div[data-testid="stPopoverBody"] {
            border-radius: 12px !important; /* Bo góc khung chat vuông vức hơn */
            border: 1px solid rgba(0, 0, 0, 0.1) !important;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2) !important;
            padding: 0 !important; 
            overflow: hidden !important;
            width: 380px !important; 
        }
    </style>
    """
    st.markdown(chat_bubble_css, unsafe_allow_html=True)
