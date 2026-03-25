import streamlit as st
import pandas as pd
# Nhập hàm cào dữ liệu từ file ssi_scraper.py
from scrapers.ssi_scraper import get_ssi_news

# Cấu hình trang cơ bản
st.set_page_config(page_title="CTCK Data Terminal", layout="wide", page_icon="📈")

st.title("📊 Terminal Quản lý & Phân tích Dịch vụ CTCK")
st.markdown("Hệ thống tự động cào tin tức, biểu phí và margin từ các công ty chứng khoán trên thị trường.")

st.divider()

st.subheader("📰 Cập nhật tin tức SSI")

# Nút bấm để kích hoạt luồng cào dữ liệu
if st.button("Cào dữ liệu SSI ngay", type="primary"):
    with st.spinner("Đang bay vào server SSI để lấy dữ liệu... 🚀"):
        df_news = get_ssi_news()
        
        if df_news is not None and not df_news.empty:
            st.success(f"Thành công! Lấy được {len(df_news)} bản tin mới nhất.")
            
            # Hiển thị bảng dữ liệu tương tác (có thể sort, kéo giãn cột)
            st.dataframe(df_news, use_container_width=True, hide_index=True)
            
            # Ý tưởng mở rộng tính năng sau này: 
            # Thêm một thanh tìm kiếm để lọc nhanh xem có bản tin nào 
            # nhắc đến việc thay đổi tỷ lệ cấp Margin của PLX hay MBB không.
        else:
            st.error("Không lấy được dữ liệu. Vui lòng kiểm tra lại cấu trúc HTML của web.")
