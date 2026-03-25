import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st

# TTL = 3600 nghĩa là hệ thống chỉ đi cào dữ liệu 1 tiếng 1 lần
@st.cache_data(ttl=3600, show_spinner="Đang đồng bộ dữ liệu từ CTCK...")
def fetch_ssi_margin_news():
    url = "https://www.ssi.com.vn/tin-tuc/tin-tuc-su-kien-ssi"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return pd.DataFrame()
            
        soup = BeautifulSoup(response.text, 'html.parser')
        news_data = []
        
        # Giả lập cào tiêu đề (Ngươi sẽ cần thay class chuẩn sau)
        articles = soup.find_all('a', class_='news-title') 
        for article in articles:
            title = article.text.strip()
            # Lọc sơ bộ: Chỉ lấy những tin có chữ "Margin", "Ký quỹ", "Phí"
            if any(keyword in title.lower() for keyword in ['margin', 'ký quỹ', 'phí']):
                link = article.get('href')
                if link.startswith('/'):
                    link = "https://www.ssi.com.vn" + link
                news_data.append({"Ngày": "Hôm nay", "Tiêu đề": title, "Link": link, "CTCK": "SSI"})
                
        return pd.DataFrame(news_data)
    except Exception as e:
        print(f"Lỗi backend: {e}")
        return pd.DataFrame()
