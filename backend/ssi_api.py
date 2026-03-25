import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import time

# Cache dữ liệu trong 1 giờ (3600 giây). Giúp web load tức thì và không bị SSI chặn IP.
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ssi_news():
    url = "https://www.ssi.com.vn/tin-tuc/tin-tuc-su-kien-ssi"
    # Giả lập trình duyệt chuẩn của người dùng thật
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "vi-VN,vi;q=0.9"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return pd.DataFrame() # Trả về mảng rỗng nếu lỗi mạng
            
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        
        # Lấy danh sách bài viết (Dựa trên cấu trúc HTML thực tế của SSI thường dùng thẻ <a> có class tin tức)
        # Lưu ý: Nếu SSI đổi class, ta chỉ cần cập nhật dòng này
        articles = soup.find_all('a', class_='news-title', limit=10) # Chỉ lấy 10 tin mới nhất cho nhẹ
        
        for article in articles:
            title = article.text.strip()
            link = article.get('href', '')
            
            if link.startswith('/'):
                link = "https://www.ssi.com.vn" + link
                
            # Phân loại Tag tự động dựa trên từ khóa trong tiêu đề
            tag = "Tin tức"
            title_lower = title.lower()
            if "margin" in title_lower or "ký quỹ" in title_lower:
                tag = "Cập nhật Margin"
            elif "phí" in title_lower:
                tag = "Biểu phí"
            elif "ra mắt" in title_lower or "sản phẩm" in title_lower:
                tag = "Sản phẩm mới"
                
            news_list.append({
                "ctck": "SSI",
                "tag": tag,
                "title": title,
                "link": link,
                "date": "Mới cập nhật" # Tạm gán, vì web SSI cần click vào trong mới thấy ngày
            })
            
        return pd.DataFrame(news_list)
        
    except Exception as e:
        print(f"Lỗi Backend SSI: {e}")
        return pd.DataFrame()
