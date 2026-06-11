import streamlit as st

def apply_custom_css(is_dark=False):
    # ==========================================
    # 1. CODE GỐC CỦA NGÀI (Bảo toàn 100%)
    # ==========================================
    custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Áp dụng font chữ toàn hệ thống */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            color: #1E2329;
        }

        /* TẠM THỜI MỞ KHÓA HEADER ĐỂ HIỆN THỊ MENU SIDEBAR */
        /* header {visibility: hidden;} */
        footer {visibility: hidden;} /* Cứ giữ ẩn footer nếu Ngài muốn */
        
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
    # 2. XỬ LÝ GHI ĐÈ DARK MODE (Khi cần thiết)
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

    # ==========================================
    # 3. ĐẮP THÊM CSS ĐỊNH DẠNG BONG BÓNG CHAT iOS (Đã làm to & thêm chữ)
    # ==========================================
    chat_bubble_css = """
    <style>
        /* Ghim cố định cụm nút bấm xuống góc phải màn hình */
        div[data-testid="stPopover"] {
            position: fixed !important;
            bottom: 30px !important;
            right: 30px !important;
            z-index: 999999 !important;
        }
        
        /* Gọt nút bấm mặc định thành hình dạng mong muốn */
        div[data-testid="stPopover"] button {
            width: 80px !important; /* Tăng chiều rộng để chứa chữ */
            height: 80px !important; /* Tăng chiều cao để bong bóng to hơn */
            border-radius: 50% !important; /* Vẫn giữ hình tròn xoe */
            background: linear-gradient(135deg, #FF9500, #FF5E3A) !important;
            border: none !important;
            padding: 0 !important;
            display: flex !important;
            flex-direction: column !important; /* Xếp icon và chữ theo chiều dọc */
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 8px 24px rgba(255, 149, 0, 0.4) !important;
            transition: transform 0.2s ease !important;
        }
        
        /* Hiệu ứng nảy nhẹ khi di chuột vào */
        div[data-testid="stPopover"] button:hover {
            transform: scale(1.08) !important;
            box-shadow: 0 12px 28px rgba(255, 149, 0, 0.6) !important;
        }
        
        /* Định dạng nội dung bên trong nút (Chèn Icon và Text qua CSS) */
        /* Giấu nội dung cũ mặc định đi */
        div[data-testid="stPopover"] button p {
            display: none !important; 
        }

        /* Dùng pseudo-element ::before để vẽ Icon to */
        div[data-testid="stPopover"] button::before {
            content: "💬";
            font-size: 32px !important; /* Icon to rõ */
            color: white !important;
            line-height: 1 !important;
            margin-bottom: 2px !important;
        }

        /* Dùng pseudo-element ::after để vẽ chữ LINANCE AI BOT */
        div[data-testid="stPopover"] button::after {
            content: "LINANCE\\A AI BOT"; /* \\A tạo dòng mới nếu cần, nhưng set width to thì ko cần */
            white-space: pre-wrap; /* Cho phép xuống dòng nếu cần */
            font-size: 9px !important; /* Chữ nhỏ xinh vừa vặn */
            font-weight: 800 !important;
            color: white !important;
            text-align: center !important;
            line-height: 1.1 !important;
        }
        
        /* Xóa viền tập trung mặc định */
        div[data-testid="stPopover"] button:focus {
            outline: none !important;
        }

        /* Bo tròn góc cửa sổ Chat khi mở ra */
        div[data-testid="stPopoverBody"] {
            border-radius: 24px !important; 
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15) !important;
            padding: 0 !important; 
            overflow: hidden !important;
            width: 380px !important; /* Cố định độ rộng khung Chat */
        }
    </style>
    """
    st.markdown(chat_bubble_css, unsafe_allow_html=True)


# ==========================================
# GỌI PHẦN HIỂN THỊ (Ngài đặt ở cuối file Dashboard)
# ==========================================

# Gọi hàm CSS (Mặc định truyền False cho Light Mode, True cho Dark Mode)
apply_custom_css(is_dark=False)

# Đường link con Bot AI chạy độc lập của Ngài
URL_APP_CHAT = "https://jtkbj9wk5udrrxvrrwpr8j.streamlit.app"

# Nút bấm mở cửa sổ chat nổi (use_container_width=False để không bị kéo giãn bậy bạ)
with st.popover("💬", use_container_width=False):
    st.components.v1.iframe(f"{URL_APP_CHAT}/?embed=true", width=380, height=550)
