import requests
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st

@st.cache_data(ttl=1800, show_spinner=False) # Làm mới dữ liệu 30 phút/lần
def fetch_mainstream_news():
    # Danh sách các luồng RSS chính thống
    sources = [
        {"name": "VnExpress", "url": "https://vnexpress.net/rss/kinh-doanh/chung-khoan.rss"},
        {"name": "CafeF", "url": "https://cafef.vn/thi-truong-chung-khoan.rss"} 
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    news_list = []
    
    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=10)
            if response.status_code == 200:
                # Đọc cấu trúc XML
                root = ET.fromstring(response.content)
                
                # Quét 10 bản tin mới nhất từ mỗi báo
                for item in root.findall('./channel/item')[:10]:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pubdate_elem = item.find('pubDate')
                    
                    title = title_elem.text.strip() if title_elem is not None else ""
                    link = link_elem.text.strip() if link_elem is not None else ""
                    pub_date = pubdate_elem.text.strip() if pubdate_elem is not None else ""
                    
                    # Hệ thống Tự động Dán nhãn (Auto-Tagging)
                    tag = "Tin vĩ mô"
                    title_lower = title.lower()
                    
                    # Bắt nhạy các tin tức liên quan đến danh mục ưu tiên hoặc dòng tiền
                    if "plx" in title_lower or "mbb" in title_lower:
                        tag = "🔥 Cổ phiếu quan tâm"
                    elif "margin" in title_lower or "ký quỹ" in title_lower or "lãi suất" in title_lower:
                        tag = "Chính sách & Dòng tiền"
                    elif "ủy ban chứng khoán" in title_lower or "ubck" in title_lower:
                        tag = "Pháp lý"
                        
                    news_list.append({
                        "ctck": source["name"], # Dùng tên báo thay cho tên CTCK
                        "tag": tag,
                        "title": title,
                        "link": link,
                        "date": pub_date[:16] # Cắt chuỗi ngày cho gọn
                    })
        except Exception as e:
            print(f"Lỗi đọc RSS từ {source['name']}: {e}")
            
    # Tạo DataFrame và trộn ngẫu nhiên hoặc xếp theo ngày (ở đây ta trả về luôn)
    df = pd.DataFrame(news_list)
    return df
