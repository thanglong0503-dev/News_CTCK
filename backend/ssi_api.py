import requests
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ssi_news():
    # Nguồn RSS cực kỳ ổn định, không chặn IP
    url = "https://vnexpress.net/rss/kinh-doanh/chung-khoan.rss"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return pd.DataFrame()
            
        # Dùng ElementTree chuyên dụng của Python để phân tích XML
        root = ET.fromstring(response.content)
        news_list = []
        
        # Quét tìm các thẻ <item> bên trong <channel>
        for item in root.findall('./channel/item')[:10]:
            title_elem = item.find('title')
            link_elem = item.find('link')
            pubdate_elem = item.find('pubDate')
            
            title = title_elem.text.strip() if title_elem is not None else ""
            link = link_elem.text.strip() if link_elem is not None else ""
            pub_date = pubdate_elem.text.strip() if pubdate_elem is not None else ""
            
            # Làm sạch chuỗi ngày tháng (Chỉ lấy phần ngày và giờ, bỏ múi giờ)
            clean_date = pub_date[:16] if len(pub_date) > 16 else pub_date
            
            # Hệ thống Auto-Tagging
            tag = "Tin thị trường"
            title_lower = title.lower()
            if "margin" in title_lower or "ký quỹ" in title_lower:
                tag = "Cập nhật Margin"
            elif "phí" in title_lower or "lãi suất" in title_lower:
                tag = "Biểu phí"
            elif "cổ phiếu" in title_lower or "vn-index" in title_lower:
                tag = "Phân tích"
                
            news_list.append({
                "ctck": "Tin Tức", 
                "tag": tag,
                "title": title,
                "link": link,
                "date": clean_date
            })
            
        return pd.DataFrame(news_list)
        
    except Exception as e:
        print(f"Lỗi Backend XML: {e}")
        return pd.DataFrame()
