import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import email.utils
from datetime import datetime

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_mainstream_news():
    news_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    # ==========================================
    # 1. CHIẾN THUẬT RSS (Cho 4 báo chính thống)
    # ==========================================
    rss_sources = [
        {"name": "CafeF", "url": "https://cafef.vn/thi-truong-chung-khoan.rss"},
        {"name": "VnExpress", "url": "https://vnexpress.net/rss/kinh-doanh/chung-khoan.rss"},
        {"name": "Báo Đầu Tư", "url": "https://baodautu.vn/chung-khoan.rss"},
        {"name": "Thanh Niên", "url": "https://thanhnien.vn/rss/kinh-te/chung-khoan.rss"}
    ]
    
    for source in rss_sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = root.findall('.//item')[:15]
                
                for item in items:
                    title_elem = item.find('title')
                    title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                    
                    link_elem = item.find('link')
                    link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                    if not link: 
                        guid_elem = item.find('guid')
                        link = guid_elem.text.strip() if guid_elem is not None and guid_elem.text else ""
                        
                    pubdate_elem = item.find('pubDate')
                    if pubdate_elem is None:
                        pubdate_elem = item.find('pubdate')
                    pub_date_str = pubdate_elem.text.strip() if pubdate_elem is not None and pubdate_elem.text else ""
                    
                    if not title or not link: continue
                        
                    clean_date = "Mới cập nhật"
                    timestamp = 0
                    if pub_date_str:
                        try:
                            parsed_date = email.utils.parsedate_to_datetime(pub_date_str)
                            clean_date = parsed_date.strftime("%d/%m/%Y %H:%M")
                            timestamp = parsed_date.timestamp()
                        except:
                            clean_date = pub_date_str[:16]
                    
                    tag = "Tin vĩ mô"
                    title_lower = title.lower()
                    if "plx" in title_lower or "mbb" in title_lower: tag = "🔥 Cổ phiếu quan tâm"
                    elif "margin" in title_lower or "ký quỹ" in title_lower: tag = "Chính sách & Dòng tiền"
                    elif "doanh nghiệp" in title_lower or "cổ tức" in title_lower: tag = "Tin doanh nghiệp"
                        
                    news_list.append({
                        "ctck": source["name"].upper(), "tag": tag, "title": title,
                        "link": link, "date": clean_date, "timestamp": timestamp
                    })
        except Exception as e:
            print(f"Lỗi RSS {source['name']}: {e}")

    # ==========================================
    # 2. CHIẾN THUẬT HTML SCAPING (Dành riêng cho Stockbiz)
    # ==========================================
    try:
        sb_url = "https://stockbiz.vn/doanh-nghiep"
        sb_res = requests.get(sb_url, headers=headers, timeout=10)
        if sb_res.status_code == 200:
            soup = BeautifulSoup(sb_res.text, 'html.parser')
            # Lùng sục toàn bộ thẻ <a> có chứa link
            links = soup.find_all('a', href=True)
            count = 0
            
            for link in links:
                if count >= 15: break # Chỉ lấy 15 tin mới nhất
                title = link.text.strip()
                href = link['href']
                
                # Bộ lọc chống rác: Tiêu đề phải dài hơn 30 ký tự (loại bỏ mấy nút bấm linh tinh)
                if len(title) > 30 and not href.startswith('javascript'):
                    full_link = "https://stockbiz.vn" + href if href.startswith('/') else href
                    
                    tag = "Tin doanh nghiệp"
                    if "plx" in title.lower() or "mbb" in title.lower(): tag = "🔥 Cổ phiếu quan tâm"
                    
                    # Vì quét HTML thô không có ngày giờ rõ ràng, ta gán giờ hiện tại để nó hiển thị lên đầu tiên
                    now = datetime.now()
                    news_list.append({
                        "ctck": "STOCKBIZ",
                        "tag": tag,
                        "title": title,
                        "link": full_link,
                        "date": now.strftime("%d/%m/%Y %H:%M"),
                        "timestamp": now.timestamp() - count # Trừ lùi để giữ đúng thứ tự bài trên web
                    })
                    count += 1
    except Exception as e:
        print(f"Lỗi HTML Stockbiz: {e}")

    # ==========================================
    # 3. TRỘN, DỌN DẸP & SẮP XẾP
    # ==========================================
    df = pd.DataFrame(news_list)
    if not df.empty and 'timestamp' in df.columns:
        # Cực kỳ quan trọng: Xóa các bài bị lặp (Do cào HTML thường dính 1 link ảnh và 1 link chữ giống hệt nhau)
        df = df.drop_duplicates(subset=['title'])
        # Sắp xếp theo dòng thời gian
        df = df.sort_values(by='timestamp', ascending=False).drop(columns=['timestamp'])
        
    return df
