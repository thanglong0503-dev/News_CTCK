import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_kafi_news():
    url = "https://kafi.vn/notification"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return pd.DataFrame()
            
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        links = soup.find_all('a', href=True)
        
        for link in links:
            title = link.text.strip()
            href = link['href']
            
            # Lọc các link rác, chỉ lấy link có text dài (thường là tiêu đề bài viết)
            if title and len(title) > 20 and not href.startswith('javascript'):
                full_link = "https://kafi.vn" + href if href.startswith('/') else href
                
                # Phân loại Tag sơ bộ
                tag = "Thông báo"
                if "margin" in title.lower() or "vay" in title.lower():
                    tag = "Cập nhật Margin"
                elif "phí" in title.lower():
                    tag = "Biểu phí"
                    
                news_list.append({
                    "ctck": "Kafi",
                    "tag": tag,
                    "title": title,
                    "link": full_link,
                    "date": "Mới cập nhật" # Tạm gán vì html thô không có ngày
                })
                
        # Loại bỏ trùng lặp và chỉ lấy 10 tin mới nhất cho nhẹ web
        df = pd.DataFrame(news_list).drop_duplicates(subset=['title']).head(10)
        return df
        
    except Exception as e:
        print(f"Lỗi Backend Kafi: {e}")
        return pd.DataFrame()
