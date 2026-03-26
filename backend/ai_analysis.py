import pandas as pd
import yfinance as yf
import re
from backend.official_news import fetch_mainstream_news

# --- PHẦN 1: ĐO LƯỜNG CẢM XÚC TIN TỨC (NEWS SENTIMENT) ---

def analyze_news_sentiment():
    # 1. Kéo dữ liệu tin tức thật
    df_news = fetch_mainstream_news()
    if df_news.empty: return 50, [] # Trả về điểm trung bình và danh sách rỗng nếu không có tin

    # 2. Định nghĩa từ khóa cảm xúc (Rule-based)
    # Tích cực (Bullish)
    positive_words = r"\b(lãi|lợi nhuận|vượt đỉnh|tăng trưởng|khả quan|đột phá|dòng tiền|mua vào|mở rộng|hấp dẫn)\b"
    # Tiêu cực (Bearish)
    negative_words = r"\b(thua lỗ|sụt giảm|nguy cơ|bắt bớ|thanh tra|margin call|bán tháo|khó khăn|yếu kém)\b"

    def get_sentiment(title):
        title_lower = title.lower()
        pos_score = len(re.findall(positive_words, title_lower))
        neg_score = len(re.findall(negative_words, title_lower))
        
        if pos_score > neg_score: return "Bullish"
        elif neg_score > pos_score: return "Bearish"
        else: return "Neutral"

    # 3. Chấm điểm từng bài báo
    df_news['sentiment'] = df_news['title'].apply(get_sentiment)

    # 4. Tính điểm tổng quan thị trường (từ 0-100)
    pos_count = len(df_news[df_news['sentiment'] == "Bullish"])
    neg_count = len(df_news[df_news['sentiment'] == "Bearish"])
    total_count = pos_count + neg_count
    
    # Điểm 50 là trung bình, >50 là tích cực, <50 là tiêu cực
    if total_count == 0: market_sentiment_score = 50
    else: market_sentiment_score = (pos_count / total_count) * 100

    # Lọc lấy 3 tin Tích cực nhất và 3 tin Tiêu cực nhất để hiển thị
    top_bullish_news = df_news[df_news['sentiment'] == "Bullish"].head(3)
    top_bearish_news = df_news[df_news['sentiment'] == "Bearish"].head(3)

    return market_sentiment_score, top_bullish_news.to_dict('records'), top_bearish_news.to_dict('records')

# --- PHẦN 2: BÁO ĐỘNG ĐIỂM MUA/BÁN KỸ THUẬT (TECHNICAL ALERTS) ---

def generate_technical_alerts():
    # Định nghĩa rổ cổ phiếu quan tâm để AI soi (Ví dụ rổ Bluechip mạnh)
    ticker_list = ["FPT.VN", "HPG.VN", "STB.VN", "VCB.VN", "SSI.VN", "MWG.VN", "DGC.VN"]
    
    alerts = []
    
    for t in ticker_list:
        try:
            # Hút dữ liệu giá 50 ngày qua để tính toán
            ticker = yf.Ticker(t)
            hist = ticker.history(period="50d")
            
            if len(hist) < 20: continue # Không đủ dữ liệu
            
            close_today = float(hist['Close'].iloc[-1])
            volume_today = float(hist['Volume'].iloc[-1])
            ma20 = float(hist['Close'].rolling(window=20).mean().iloc[-1])
            volume_ma10 = float(hist['Volume'].rolling(window=10).mean().iloc[-1])

            # 1. Kiểm tra điểm nổ (Breakout): Giá vượt MA20 và Volume bùng nổ
            if close_today > ma20 and volume_today > 1.5 * volume_ma10:
                alerts.append({
                    "ticker": t.replace(".VN", ""),
                    "type": "Nổ Vol. Vượt đỉnh",
                    "color": "#0ECB81",
                    "details": f"Giá: {close_today:,.0f} | Vol: {volume_today/1e6:,.1f} tr cổ (+{(volume_today/volume_ma10-1)*100:.0f}%)"
                })

            # 2. Kiểm tra điểm Quá bán (Oversold - Rơi sâu vào vùng giá rẻ)
            # Giả định nếu giá rớt xuống dưới đường MA20 hơn 5% là cơ hội xem xét
            if close_today < ma20 * 0.95:
                alerts.append({
                    "ticker": t.replace(".VN", ""),
                    "type": "Cơ hội bắt đáy",
                    "color": "#F6465D",
                    "details": f"Giá: {close_today:,.0f} | Thấp hơn 5% so với giá TB tháng (MA20)"
                })
        except: continue

    # Giới hạn lấy 5 báo động mới nhất
    return alerts[:5]
