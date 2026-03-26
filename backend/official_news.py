import requests
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st
import email.utils

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_mainstream_news():
    sources = [
        {"name": "CafeF", "url": "https://cafef.vn/thi-truong-chung-khoan.rss"},
        {"name": "VnExpress", "url": "https://vnexpress.net/rss/kinh-doanh/chung-khoan.rss"},
        {"name": "Báo Đầu Tư", "url": "https://baodautu.vn/chung-khoan.rss"},
        {"name": "Thanh Niên", "url": "https://thanhnien.vn/rss/kinh-te/chung-khoan.rss"}
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*"
    }
    news_list = []
    
    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=10)
            if response.status_code == 200:
                # Dùng ElementTree để bảo toàn nguyên vẹn Tiêu đề (CDATA)
                root = ET.fromstring(response.content)
                
                # Tuyệt kỹ XPath './/item': Quét sạch mọi ngóc ngách tìm bản tin
                items = root.findall('.//item')[:15]
                
                for item in items:
                    # Rút trích Tiêu đề
                    title_elem = item.find('title')
                    title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                    
                    # Rút trích Link
                    link_elem = item.find('link')
                    link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                    if not link: 
                        guid_elem = item.find('guid')
                        link = guid_elem.text.strip() if guid_elem is not None and guid_elem.text else ""
                        
                    # Rút trích Ngày tháng
                    pubdate_elem = item.find('pubDate') 
                    if pubdate_elem is None:
                        pubdate_elem = item.find('pubdate')
                    pub_date_str = pubdate_elem.text.strip() if pubdate_elem is not None and pubdate_elem.text else ""
                    
                    # Nếu báo bị lỗi mất tiêu đề hoặc link thì bỏ qua dòng đó
                    if not title or not link:
                        continue
                        
                    # 1. Thuật toán thời gian
                    clean_date = "Mới cập nhật"
                    timestamp = 0
                    if pub_date_str:
                        try:
                            parsed_date = email.utils.parsedate_to_datetime(pub_date_str)
                            clean_date = parsed_date.strftime("%d/%m/%Y %H:%M")
                            timestamp = parsed_date.timestamp()
                        except:
                            clean_date = pub_date_str[:16]
                    
                    # 2. Thuật toán dán nhãn thông minh (Auto-Tagging)
                    tag = "Tin vĩ mô"
                    title_lower = title.lower()
                    
                    if "plx" in title_lower or "mbb" in title_lower:
                        tag = "🔥 Cổ phiếu quan tâm"
                    elif "margin" in title_lower or "ký quỹ" in title_lower or "lãi suất" in title_lower:
                        tag = "Chính sách & Dòng tiền"
                    elif "ủy ban chứng khoán" in title_lower or "ubck" in title_lower:
                        tag = "Pháp lý"
                        
                    news_list.append({
                        "ctck": source["name"].upper(),
                        "tag": tag,
                        "title": title,
                        "link": link,
                        "date": clean_date,
                        "timestamp": timestamp
                    })
        except Exception as e:
            print(f"Bỏ qua {source['name']} do lỗi: {e}")
            
    df = pd.DataFrame(news_list)
    
    # 3. Trộn và sắp xếp thời gian chuẩn xác
    if not df.empty and 'timestamp' in df.columns:
        df = df.sort_values(by='timestamp', ascending=False).drop(columns=['timestamp'])
        
    return df
