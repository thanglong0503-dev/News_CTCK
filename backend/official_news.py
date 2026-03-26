import requests
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st
import email.utils # Thư viện zin của Python chuyên dịch ngày tháng RSS

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_mainstream_news():
    # Danh sách "Hạm đội" RSS Chứng khoán
    sources = [
        {"name": "CafeF", "url": "https://cafef.vn/thi-truong-chung-khoan.rss"},
        {"name": "VnExpress", "url": "https://vnexpress.net/rss/kinh-doanh/chung-khoan.rss"},
        {"name": "Vietstock", "url": "https://vietstock.vn/rss/chung-khoan.rss"},
        {"name": "VnEconomy", "url": "https://vneconomy.vn/rss/chung-khoan.rss"}
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    news_list = []
    
    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                # Quét 10 bản tin mới nhất từ mỗi nguồn
                for item in root.findall('./channel/item')[:10]:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pubdate_elem = item.find('pubDate')
                    
                    title = title_elem.text.strip() if title_elem is not None else ""
                    link = link_elem.text.strip() if link_elem is not None else ""
                    pub_date_str = pubdate_elem.text.strip() if pubdate_elem is not None else ""
                    
                    # 1. THUẬT TOÁN CHUẨN HÓA NGÀY THÁNG
                    clean_date = "Mới cập nhật"
                    timestamp = 0
                    if pub_date_str:
                        try:
                            # Dịch chuỗi RSS (RFC 2822) thành Object Thời gian thực
                            parsed_date = email.utils.parsedate_to_datetime(pub_date_str)
                            # Format lại cho đẹp: Ngày/Tháng/Năm Giờ:Phút
                            clean_date = parsed_date.strftime("%d/%m/%Y %H:%M")
                            # Lấy tem thời gian (giây) để lát nữa sắp xếp
                            timestamp = parsed_date.timestamp()
                        except:
                            clean_date = pub_date_str[:16] # Kế hoạch B nếu parse lỗi
                    
                    # 2. HỆ THỐNG AUTO-TAGGING & LỌC TỪ KHÓA
                    tag = "Tin vĩ mô"
                    title_lower = title.lower()
                    
                    if "plx" in title_lower or "mbb" in title_lower:
                        tag = "🔥 Cổ phiếu quan tâm"
                    elif "margin" in title_lower or "ký quỹ" in title_lower or "phí" in title_lower:
                        tag = "Chính sách & Dòng tiền"
                    elif "ủy ban chứng khoán" in title_lower or "ubck" in title_lower:
                        tag = "Pháp lý"
                        
                    news_list.append({
                        "ctck": source["name"],
                        "tag": tag,
                        "title": title,
                        "link": link,
                        "date": clean_date,
                        "timestamp": timestamp # Cột ẩn dùng để Sort
                    })
        except Exception as e:
            print(f"Lỗi đọc RSS từ {source['name']}: {e}")
            
    df = pd.DataFrame(news_list)
    
    # 3. SẮP XẾP TIN MỚI NHẤT LÊN ĐẦU TIÊN
    if not df.empty and 'timestamp' in df.columns:
        # Sort theo timestamp giảm dần, sau đó xóa cột timestamp đi cho sạch data
        df = df.sort_values(by='timestamp', ascending=False).drop(columns=['timestamp'])
        
    return df
