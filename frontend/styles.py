import streamlit as st

# ==========================================
# CẤU HÌNH TRANG & CÔNG TẮC GIAO DIỆN
# ==========================================
st.set_page_config(page_title="LINANCE Dashboard", layout="wide")

# Tạo một công tắc trên Sidebar để Ngài chuyển đổi Sáng/Tối
dark_mode = st.sidebar.toggle("🌙 Giao diện Tối (Dark Mode)", value=False)

# ==========================================
# LÕI CSS XỬ LÝ GIAO DIỆN (LIGHT & DARK TONE)
# ==========================================
def apply_custom_css(is_dark):
    # 1. KHAI BÁO BỘ MÀU SÁNG (Light Theme)
    light_colors = """
        :root {
            --bg-main: #FAFAFA;
            --text-title: #1E2329;
            --text-desc: #474D57;
            --text-meta: #848E9C;
            --card-bg: #FFFFFF;
            --card-border: #EAECEF;
            --card-hover: #FCD535; /* Màu vàng nhấn đặc trưng */
            --tag-bg: #F5F5F5;
        }
    """
    
    # 2. KHAI BÁO BỘ MÀU TỐI (Dark Theme)
    dark_colors = """
        :root {
            --bg-main: #0B0E11; /* Đen nhám sang trọng kiểu Binance */
            --text-title: #EAECEF;
            --text-desc: #848E9C;
            --text-meta: #5E6673;
            --card-bg: #181A20;
            --card-border: #2B3139;
            --card-hover: #FCD535; /* Giữ nguyên vàng nhấn cho nổi bật */
            --tag-bg: #2B3139;
        }
    """

    # Luân chuyển bộ màu dựa trên công tắc
    theme_colors = dark_colors if is_dark else light_colors

    # 3. ÁP DỤNG BIẾN MÀU VÀO CẤU TRÚC CSS
    custom_css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Nạp bộ màu vào hệ thống */
        {theme_colors}

        /* Áp dụng font chữ toàn hệ thống */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif !important;
            color: var(--text-title) !important;
            transition: background-color 0.4s ease, color 0.4s ease; /* Hiệu ứng chuyển màu mượt mà */
        }}

        /* Ẩn Footer mặc định của Streamlit (ĐÃ GIẢI PHÓNG HEADER) */
        footer {{visibility: hidden;}}
        
        /* Chỉnh màu nền chính của App */
        .stApp {{ background-color: var(--bg-main); }}

        /* Định dạng các component UI */
        .category-tag {{ 
            background-color: var(--tag-bg); 
            color: var(--text-desc); 
            padding: 4px 12px; 
            border-radius: 4px; 
            font-size: 14px; 
            font-weight: 500; 
            display: inline-block; 
            margin-bottom: 16px;
            transition: all 0.4s ease;
        }}
        
        .hero-title {{ font-size: 40px; font-weight: 700; line-height: 1.2; color: var(--text-title); margin-bottom: 16px; transition: color 0.4s ease; }}
        .hero-desc {{ font-size: 16px; color: var(--text-desc); line-height: 1.5; margin-bottom: 24px; transition: color 0.4s ease; }}
        .hero-meta {{ font-size: 14px; color: var(--text-title); font-weight: 600; }}
        .hero-hashtag {{ font-size: 14px; color: var(--text-desc); font-weight: 400; margin-left: 12px; }}

        /* CSS cho thanh tiêu đề danh sách */
        .section-title {{ font-size: 24px; font-weight: 700; color: var(--text-title); margin-top: 48px; margin-bottom: 24px; transition: color 0.4s ease; }}

        /* CSS cho các thẻ bài viết (Cards) */
        .news-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.3s ease-in-out;
            cursor: pointer;
            height: 100%;
        }}
        .news-card:hover {{
            border-color: var(--card-hover);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15); /* Đổ bóng sâu hơn khi hover */
            transform: translateY(-4px); /* Nảy lên cao hơn một chút */
        }}
        .card-tag {{ font-size: 12px; font-weight: 500; color: var(--text-meta); text-transform: uppercase; margin-bottom: 12px; transition: color 0.4s ease; }}
        .card-title {{ font-size: 18px; font-weight: 600; color: var(--text-title); margin-bottom: 12px; line-height: 1.4; transition: color 0.4s ease; }}
        .card-date {{ font-size: 14px; color: var(--text-meta); transition: color 0.4s ease; }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# Khởi chạy CSS
apply_custom_css(dark_mode)

# ==========================================
# KIỂM THỬ GIAO DIỆN (Ngài có thể xóa phần này sau khi test)
# ==========================================
st.markdown('<div class="hero-title">LINANCE Terminal</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-desc">Hệ thống phân tích và quản trị danh mục đầu tư chuyên nghiệp. Dữ liệu RS_DATA được cập nhật theo thời gian thực.</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Tin tức thị trường nổi bật</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('''
    <div class="news-card">
        <div class="card-tag">PHÂN TÍCH KỸ THUẬT</div>
        <div class="card-title">HPG bứt phá khỏi vùng tích lũy, khối lượng giao dịch tăng đột biến</div>
        <div class="card-date">11 Tháng 6, 2026</div>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown('''
    <div class="news-card">
        <div class="card-tag">VĨ MÔ</div>
        <div class="card-title">Tín hiệu mới từ chính sách điều hành lãi suất</div>
        <div class="card-date">11 Tháng 6, 2026</div>
    </div>
    ''', unsafe_allow_html=True)
