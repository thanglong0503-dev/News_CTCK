import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ssi_news():
    # Sử dụng chuẩn RSS Feed công khai thay vì cào HTML lậu để tránh Firewall
    url = "https://cafef.vn/tin-tuc-chung.rss"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return pd.DataFrame()
            
        # Dùng BeautifulSoup đọc luồng XML/RSS
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        
        # Cắt lấy 10 bản tin mới nhất
        items = soup.find_all('item', limit=10)
        
        for item in items:
            title = item.find('title').text.strip() if item.find('title') else ""
            link = item.find('link').text.strip() if item.find('link') else ""
            pub_date = item.find('pubdate').text.strip() if item.find('pubdate') else ""
            
            # Xử lý cắt chuỗi ngày tháng cho đẹp (Bỏ múi giờ GMT)
            clean_date = pub_date[:16] if len(pub_date) > 16 else pub_date
            
            # Hệ thống Auto-Tagging (Dán nhãn tự động)
            tag = "Tin thị trường"
            title_lower = title.lower()
            if "margin" in title_lower or "ký quỹ" in title_lower:
                tag = "Cập nhật Margin"
            elif "phí" in title_lower or "lãi suất" in title_lower:
                tag = "Biểu phí"
            elif "ctck" in title_lower or "chứng khoán" in title_lower:
                tag = "Tin CTCK"
                
            news_list.append({
                "ctck": "Thị trường", 
                "tag": tag,
                "title": title,
                "link": link,
                "date": clean_date
            })
            
        return pd.DataFrame(news_list)
        
    except Exception as e:
        print(f"Lỗi Backend RSS: {e}")
        return pd.DataFrame()
