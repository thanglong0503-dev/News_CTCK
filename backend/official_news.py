import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import email.utils

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_mainstream_news():
    # Danh sách các luồng RSS mượt và không chặn IP
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
            # Gửi request xin dữ liệu
            response = requests.get(source["url"], headers=headers, timeout=15)
            if response.status_code == 200:
                # Dùng BeautifulSoup cày nát HTML/XML để bóc tách
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # html.parser tự động chuyển mọi thẻ thành chữ thường, nên pubDate thành pubdate
                items = soup.find_all('item')[:15] # Lấy tận 15 tin nóng nhất từ MỖI BÁO
                
                for item in items:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pubdate_elem = item.find('pubdate')
                    
                    title = title_elem.text.strip() if title_elem else ""
                    link = link_elem.text.strip() if link_elem else ""
                    # Nếu báo giấu link ở thẻ khác, tìm thử guid
                    if not link and item.find('guid'):
                        link = item.find('guid').text.strip()
                        
                    pub_date_str = pubdate_elem.text.strip() if pubdate_elem else ""
                    
                    # Bỏ qua nếu dòng tin bị lỗi rỗng
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
    
    # 3. Trộn toàn bộ tin của các báo và sắp xếp theo số giây gần nhất
    if not df.empty and 'timestamp' in df.columns:
        df = df.sort_values(by='timestamp', ascending=False).drop(columns=['timestamp'])
        
    return df
