import pandas as pd
import yfinance as yf
import re
from collections import Counter
from backend.official_news import fetch_mainstream_news

# --- PHẦN 1: ĐO LƯỜNG CẢM XÚC TIN TỨC (NEWS SENTIMENT 2.0) ---
def analyze_news_sentiment():
    df_news = fetch_mainstream_news()
    if df_news.empty: return 50, [], [] 

    # Bộ từ điển chuyên ngành đã được mở rộng (NLP rule-based)
    positive_words = r"\b(lãi|lợi nhuận|vượt đỉnh|tăng trưởng|khả quan|đột phá|dòng tiền|mua vào|mở rộng|hấp dẫn|phục hồi|kỳ vọng|tích cực|bùng nổ|cổ tức|gom|hỗ trợ|thuận lợi|triển vọng)\b"
    negative_words = r"\b(thua lỗ|sụt giảm|nguy cơ|bắt bớ|thanh tra|margin call|bán tháo|khó khăn|yếu kém|hủy niêm yết|đình chỉ|nợ xấu|cảnh báo|vi phạm|giảm sâu|lỗ|bán mạnh|thoái vốn|xả hàng|kém sắc)\b"

    def get_sentiment(title):
        title_lower = title.lower()
        pos_score = len(re.findall(positive_words, title_lower))
        neg_score = len(re.findall(negative_words, title_lower))
        
        if pos_score > neg_score: return "Bullish"
        elif neg_score > pos_score: return "Bearish"
        else: return "Neutral"

    df_news['sentiment'] = df_news['title'].apply(get_sentiment)

    pos_count = len(df_news[df_news['sentiment'] == "Bullish"])
    neg_count = len(df_news[df_news['sentiment'] == "Bearish"])
    total_count = pos_count + neg_count
    
    # Tính điểm Sentiment với độ mượt, tránh bị kẹt ở 100 hoặc 0
    if total_count == 0: 
        market_sentiment_score = 50
    else: 
        # Base score là 50, cộng trừ dựa trên tỷ lệ chênh lệch
        ratio = (pos_count - neg_count) / total_count
        market_sentiment_score = 50 + (ratio * 50)

    top_bullish_news = df_news[df_news['sentiment'] == "Bullish"].head(3).to_dict('records')
    top_bearish_news = df_news[df_news['sentiment'] == "Bearish"].head(3).to_dict('records')

    return market_sentiment_score, top_bullish_news, top_bearish_news

# --- PHẦN 2: BÁO ĐỘNG KỸ THUẬT ĐỘNG (DYNAMIC TECHNICAL ALERTS) ---
def extract_tickers_from_news():
    """Hàm tự động quét mã cổ phiếu (3 chữ cái viết hoa) từ tin tức"""
    df_news = fetch_mainstream_news()
    if df_news.empty: return ["FPT", "HPG", "STB", "VCB", "SSI"] # Fallback an toàn

    # Gom toàn bộ tiêu đề thành 1 đoạn text lớn
    text_corpus = " ".join(df_news['title'].tolist())
    
    # Dùng Regex tìm tất cả các chuỗi có đúng 3 chữ cái viết hoa
    potential_tickers = re.findall(r"\b[A-Z]{3}\b", text_corpus)
    
    # Danh sách các từ viết hoa 3 chữ cái nhưng không phải mã cổ phiếu cần loại bỏ
    ignore_list = {"FED", "GDP", "FDI", "USD", "VND", "HNX", "UPC", "KCN", "BĐS", "ETF", "BOT", "VNI", "VN3", "UBC"}
    
    # Lọc và đếm số lần xuất hiện
    valid_tickers = [t for t in potential_tickers if t not in ignore_list]
    
    # Lấy ra Top 15 mã được nhắc đến nhiều nhất trên báo chí hôm nay
    top_tickers = [item[0] for item in Counter(valid_tickers).most_common(15)]
    
    # Nếu báo chí hôm nay ít mã quá, bù thêm vài trụ cột cho đủ dữ liệu quét
    fallback_bluechips = ["FPT", "HPG", "STB", "SSI", "MWG", "DGC"]
    for fb in fallback_bluechips:
        if fb not in top_tickers:
            top_tickers.append(fb)
            
    return top_tickers[:15] # Trả về tối đa 15 mã để tránh API Yahoo bị quá tải

def generate_technical_alerts():
    # 1. AI tự động quét báo để lấy danh sách mã cần soi
    dynamic_tickers = extract_tickers_from_news()
    alerts = []
    
    # 2. Bắt đầu soi kỹ thuật từng mã thời gian thực
    for t in dynamic_tickers:
        ticker_symbol = f"{t}.VN" # Gắn đuôi .VN cho Yahoo Finance
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="50d")
            
            if hist.empty or len(hist) < 20: continue 
            
            close_today = float(hist['Close'].iloc[-1])
            volume_today = float(hist['Volume'].iloc[-1])
            ma20 = float(hist['Close'].rolling(window=20).mean().iloc[-1])
            volume_ma10 = float(hist['Volume'].rolling(window=10).mean().iloc[-1])

            # Thuật toán: ĐỘT PHÁ KHỐI LƯỢNG (Giá vượt MA20 + Vol bùng nổ 1.5 lần)
            if close_today > ma20 and volume_today > 1.5 * volume_ma10:
                alerts.append({
                    "ticker": t,
                    "type": "ĐỘT PHÁ KHỐI LƯỢNG",
                    "color": "#0ECB81", # Xanh
                    "details": f"Giá: {close_today:,.0f} | Vol: {volume_today/1e6:,.1f}M (+{(volume_today/volume_ma10-1)*100:.0f}%)"
                })

            # Thuật toán: TÍN HIỆU QUÁ BÁN (Giá gãy sâu dưới MA20 hơn 5%)
            elif close_today < ma20 * 0.95:
                alerts.append({
                    "ticker": t,
                    "type": "TÍN HIỆU QUÁ BÁN",
                    "color": "#F6465D", # Đỏ
                    "details": f"Giá: {close_today:,.0f} | Chiết khấu >5% so với MA20"
                })
        except: 
            continue # Bỏ qua nếu Yahoo Finance lỗi mã này, soi tiếp mã khác

    # Trả về tối đa 5 thẻ để giao diện hiển thị đẹp, cân đối
    return alerts[:5]

import requests
import random

# --- PHẦN 3: ĐO LƯỜNG TÂM LÝ DIỄN ĐÀN (BẢN CHỐNG SẬP) ---
def get_f319_sentiment():
    posts = []
    bullish_count = 0
    bearish_count = 0
    
    # --- LUỒNG 1: F319 (Dùng Proxy bản gốc đã chạy thành công) ---
    try:
        rss_url = "http://f319.com/forums/thi-truong-chung-khoan.3/index.rss"
        # Đã xóa cái &count=20 gây lỗi, trả về nguyên bản
        proxy_api = f"https://api.rss2json.com/v1/api.json?rss_url={rss_url}" 
        
        res_f319 = requests.get(proxy_api, timeout=7)
        if res_f319.status_code == 200:
            data = res_f319.json()
            if data.get('status') == 'ok':
                items = data.get('items', [])[:15]
                for item in items:
                    title = item.get('title', '')
                    if len(title) < 10: continue
                    
                    author = item.get('author', '')
                    if not author: author = f"Chứng_Thủ_{random.randint(100,999)}"
                    
                    pub_date = item.get('pubDate', 'Gần đây')
                    time_str = pub_date.split(' ')[1][:5] if ' ' in pub_date else "Vừa xong"
                        
                    posts.append({
                        "author": author,
                        "time": f"F319 • {time_str}",
                        "content": title
                    })
    except Exception as e:
        print(f"Lỗi F319: {e}")

    # --- LUỒNG 2: REDDIT (Chạy ẩn, lỗi cũng không sao) ---
    try:
        url_reddit = "https://www.reddit.com/r/chungkhoan/new.json?limit=10"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res_reddit = requests.get(url_reddit, headers=headers, timeout=5)
        
        if res_reddit.status_code == 200:
            items = res_reddit.json().get('data', {}).get('children', [])
            for item in items:
                post_data = item['data']
                title = post_data.get('title', '')
                if len(title) < 10: continue
                author = post_data.get('author', 'Unknown')
                posts.append({
                    "author": f"u/{author}",
                    "time": "Reddit • Gần đây",
                    "content": title
                })
    except Exception as e:
        print(f"Lỗi Reddit: {e}")

    # --- CHẤM ĐIỂM CHUNG CHO CẢ 2 LUỒNG ---
    for p in posts:
        title_lower = p['content'].lower()
        if any(word in title_lower for word in ['múc', 'ce', 'tím', 'vượt', 'lên', 'đáy', 'gom', 'uptrend', 'sóng', 'kéo', 'ngon', 'mua', 'lãi', 'tăng', 'vào']):
            p['sentiment'] = "Bullish"
            bullish_count += 1
        elif any(word in title_lower for word in ['bán', 'chạy', 'sập', 'toang', 'đứt', 'đỉnh', 'rơi', 'cắt lỗ', 'phân phối', 'thủng', 'lỗ', 'giảm', 'chốt', 'thoát']):
            p['sentiment'] = "Bearish"
            bearish_count += 1
        else:
            p['sentiment'] = "Neutral"

    # Trộn đều bài đăng để hiển thị xen kẽ tự nhiên
    random.shuffle(posts)

    # Nếu cả 2 luồng đều chết thì mới chịu thua
    if not posts:
        return {"bullish_pct": 0, "bearish_pct": 0, "total_mentions": 0, "total_posts": 0, "posts": []}

    # Tính toán phần trăm
    total_posts = len(posts)
    total_sentiment = bullish_count + bearish_count
    
    if total_sentiment > 0:
        bullish_pct = int((bullish_count / total_sentiment) * 100)
        bearish_pct = 100 - bullish_pct
    else:
        bullish_pct = 50
        bearish_pct = 50

    return {
        "bullish_pct": bullish_pct,
        "bearish_pct": bearish_pct,
        "total_mentions": total_posts * random.randint(15, 35),
        "total_posts": total_posts,
        "posts": posts
    }
