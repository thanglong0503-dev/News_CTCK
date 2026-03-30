import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import email.utils
from datetime import datetime
import re # ĐÃ THÊM: Thư viện Regex để xử lý chuỗi lọc trùng

# ==========================================
# 0. TRẠM KIỂM DUYỆT TIN CHẤN ĐỘNG (RULE-BASED NLP)
# ==========================================
def apply_hot_news_filter(df):
    if df.empty or 'title' not in df.columns:
        return df

    # "Từ điển tử thần" - Bản Song Ngữ
    hot_keywords = [
        # Tiếng Việt
        'khởi tố', 'bắt giam', 'thanh tra', 'thao túng', 'hủy niêm yết', 'đình chỉ', 'vi phạm', 'kỷ luật', 'cảnh báo',
        'kỷ lục', 'đột biến', 'báo lỗ', 'phá sản', 'sáp nhập', 'thoái vốn', 'giải thể', 'cổ tức khủng', 'thương vụ',
        'lãi suất', 'hút tiền', 'bơm tiền', 'nhnn', 'ngân hàng nhà nước', 'tỷ giá', 'fed', 'khủng hoảng', 'lạm phát',
        # Tiếng Anh
        'crash', 'bankrupt', 'bankruptcy', 'rate cut', 'inflation', 'merger', 'acquisition', 'sec', 'lawsuit', 'plunges', 'soars', 'crisis', 'layoff'
    ]
    
    def check_hot(row):
        title_lower = str(row['title']).lower()
        if any(kw in title_lower for kw in hot_keywords):
            return '🔥 TIN CHẤN ĐỘNG'
        return row['tag'] 

    df['tag'] = df.apply(check_hot, axis=1)
    df['is_hot'] = df['tag'].str.contains('🔥').astype(int)
    df = df.sort_values(by=['is_hot', 'timestamp'], ascending=[False, False]).drop(columns=['is_hot'])
    return df

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_mainstream_news():
    news_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    # ==========================================
    # 1. CHIẾN THUẬT RSS (TRONG NƯỚC & QUỐC TẾ)
    # ==========================================
    rss_sources = [
        # Nguồn VN
        {"name": "CafeF", "url": "https://cafef.vn/thi-truong-chung-khoan.rss", "region": "VN"},
        {"name": "VnExpress", "url": "https://vnexpress.net/rss/kinh-doanh/chung-khoan.rss", "region": "VN"},
        {"name": "Báo Đầu Tư", "url": "https://baodautu.vn/chung-khoan.rss", "region": "VN"},
        {"name": "Thanh Niên", "url": "https://thanhnien.vn/rss/kinh-te/chung-khoan.rss", "region": "VN"},
        # Nguồn Quốc Tế
        {"name": "CNBC", "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", "region": "GLOBAL"},
        {"name": "Yahoo", "url": "https://finance.yahoo.com/news/rss", "region": "GLOBAL"}
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
                    
                    title_lower = title.lower()
                    if source["region"] == "GLOBAL":
                        tag = "Tin Quốc Tế"
                    else:
                        tag = "Tin vĩ mô"
                        if "plx" in title_lower or "mbb" in title_lower: tag = "🔥 Cổ phiếu quan tâm"
                        elif "margin" in title_lower or "ký quỹ" in title_lower: tag = "Chính sách & Dòng tiền"
                        elif "doanh nghiệp" in title_lower or "cổ tức" in title_lower: tag = "Tin doanh nghiệp"
                        
                    news_list.append({
                        "ctck": source["name"].upper(), "tag": tag, "title": title,
                        "link": link, "date": clean_date, "timestamp": timestamp, "region": source["region"] 
                    })
        except Exception as e:
            print(f"Lỗi RSS {source['name']}: {e}")

    # ==========================================
    # 2. CHIẾN THUẬT HTML (Stockbiz - Nguồn VN)
    # ==========================================
    try:
        sb_url = "https://stockbiz.vn/doanh-nghiep"
        sb_res = requests.get(sb_url, headers=headers, timeout=10)
        if sb_res.status_code == 200:
            soup = BeautifulSoup(sb_res.text, 'html.parser')
            links = soup.find_all('a', href=True)
            count = 0
            
            for link in links:
                if count >= 15: break
                title = link.text.strip()
                href = link['href']
                
                if len(title) > 30 and not href.startswith('javascript'):
                    full_link = "https://stockbiz.vn" + href if href.startswith('/') else href
                    tag = "Tin doanh nghiệp"
                    if "plx" in title.lower() or "mbb" in title.lower(): tag = "🔥 Cổ phiếu quan tâm"
                    
                    now = datetime.now()
                    news_list.append({
                        "ctck": "STOCKBIZ", "tag": tag, "title": title,
                        "link": full_link, "date": now.strftime("%d/%m/%Y %H:%M"),
                        "timestamp": now.timestamp() - count, "region": "VN" 
                    })
                    count += 1
    except Exception as e:
        print(f"Lỗi HTML Stockbiz: {e}")

    # ==========================================
    # 3. TRỘN, DỌN DẸP LỌC TRÙNG & SẮP XẾP BẰNG AI
    # ==========================================
    df = pd.DataFrame(news_list)
    if not df.empty and 'timestamp' in df.columns:
        
        # --- BỘ LỌC TRÙNG LẶP THÔNG MINH ---
        def normalize_title(text):
            # Xóa các tiền tố mã cổ phiếu (VD: "CMX: ", "VAF - ")
            text = re.sub(r'^([A-Za-z0-9]{3,4}\s*[:\-]\s*)', '', str(text))
            text = text.lower().strip()
            # Xóa toàn bộ dấu câu để so khớp chữ
            text = re.sub(r'[^\w\s]', '', text) 
            return text

        # Tạo cột tạm chứa tiêu đề đã làm sạch
        df['clean_title'] = df['title'].apply(normalize_title)
        
        # Đánh trọng số: STOCKBIZ = 1 (VIP), các báo khác = 2 (Thường)
        df['priority'] = df['ctck'].apply(lambda x: 1 if x == 'STOCKBIZ' else 2)
        
        # Sắp xếp: Ưu tiên VIP, sau đó ưu tiên tin mới nhất
        df = df.sort_values(by=['priority', 'timestamp'], ascending=[True, False])
        
        # Càn quét trùng lặp dựa trên clean_title, giữ lại bản của VIP
        df = df.drop_duplicates(subset=['clean_title'], keep='first')
        
        # Dọn rác
        df = df.drop(columns=['clean_title', 'priority'])
        
        # Đưa qua trạm kiểm duyệt AI
        df = apply_hot_news_filter(df) 
        
        if 'timestamp' in df.columns:
            df = df.drop(columns=['timestamp'])
            
    return df
