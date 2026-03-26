import yfinance as yf
import streamlit as st

@st.cache_data(ttl=300, show_spinner=False)
def fetch_realtime_data():
    # Phân bổ 4 cột dữ liệu theo đúng ý ngươi
    groups = {
        "Vĩ mô & Chỉ số": ["^VNINDEX", "VND=X", "GC=F"],
        "Danh mục Tích sản": ["PLX.VN", "MBB.VN", "TNG.VN"],
        "Top Công Nghệ": ["FPT.VN", "CMG.VN", "VGI.VN"],
        "Volume Lớn nhất": ["SSI.VN", "VND.VN", "HPG.VN"]
    }

    # Bảng mapping tên đẹp và Icon (Icon dùng Emoji để chạy mượt 100% không bị lỗi link ảnh)
    meta = {
        "^VNINDEX": {"name": "VNINDEX", "icon": "🇻🇳"},
        "VND=X": {"name": "USD/VND", "icon": "💵"},
        "GC=F": {"name": "VÀNG", "icon": "🥇"},
        "PLX.VN": {"name": "PLX", "icon": "⛽"},
        "MBB.VN": {"name": "MBB", "icon": "🏦"},
        "TNG.VN": {"name": "TNG", "icon": "👕"},
        "FPT.VN": {"name": "FPT", "icon": "💻"},
        "CMG.VN": {"name": "CMG", "icon": "🌐"},
        "VGI.VN": {"name": "VGI", "icon": "📡"},
        "SSI.VN": {"name": "SSI", "icon": "📈"},
        "VND.VN": {"name": "VND", "icon": "📊"},
        "HPG.VN": {"name": "HPG", "icon": "🏗️"}
    }

    market_data = {}
    for t in meta.keys():
        try:
            # Hút dữ liệu 5 ngày qua để so sánh giá hôm nay và hôm qua
            ticker = yf.Ticker(t)
            hist = ticker.history(period="5d")
            if len(hist) >= 2:
                close_today = float(hist['Close'].iloc[-1])
                close_prev = float(hist['Close'].iloc[-2])
                change_pct = ((close_today - close_prev) / close_prev) * 100

                # Cân đối hiển thị (Giá to thì phẩy ngàn, giá bé thì lấy số thập phân)
                if close_today > 1000: price_str = f"{close_today:,.0f}"
                else: price_str = f"{close_today:,.2f}"
            else:
                price_str = "0.00"
                change_pct = 0.0

            market_data[t] = {
                "name": meta[t]["name"],
                "icon": meta[t]["icon"],
                "price": f"${price_str}" if "USD" in t else price_str,
                "change": change_pct
            }
        except:
            market_data[t] = {"name": meta[t]["name"], "icon": meta[t]["icon"], "price": "N/A", "change": 0.0}

    return market_data, groups
