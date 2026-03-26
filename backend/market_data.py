import yfinance as yf
import streamlit as st

@st.cache_data(ttl=300, show_spinner=False)
def fetch_realtime_data():
    # Cấu trúc 4 cột theo đúng chuẩn Terminal
    groups = {
        "Tổng quan thị trường": ["^VNINDEX", "GC=F", "VND=X", "BZ=F", "^IXIC"],
        "Vốn hóa lớn": ["VCB.VN", "BID.VN", "FPT.VN", "HPG.VN"],
        "Top SMG (Momentum)": ["DGC.VN", "GMD.VN", "MWG.VN", "SSI.VN"],
        "Volume Lớn nhất": ["NVL.VN", "STB.VN", "SHB.VN", "VND.VN"]
    }

    # Đổi tên hiển thị cho chuyên nghiệp (Không dùng Icon nữa)
    meta = {
        "^VNINDEX": "VNINDEX", "GC=F": "VÀNG (Gold)", "VND=X": "USD/VND", 
        "BZ=F": "DẦU BRENT", "^IXIC": "NASDAQ",
        "VCB.VN": "VCB", "BID.VN": "BID", "FPT.VN": "FPT", "HPG.VN": "HPG",
        "DGC.VN": "DGC", "GMD.VN": "GMD", "MWG.VN": "MWG", "SSI.VN": "SSI",
        "NVL.VN": "NVL", "STB.VN": "STB", "SHB.VN": "SHB", "VND.VN": "VND"
    }

    market_data = {}
    for t in meta.keys():
        try:
            ticker = yf.Ticker(t)
            hist = ticker.history(period="5d")
            if not hist.empty and len(hist) >= 2:
                close_today = float(hist['Close'].iloc[-1])
                close_prev = float(hist['Close'].iloc[-2])
                change_pct = ((close_today - close_prev) / close_prev) * 100

                # Định dạng số tiền: Vàng/Nasdaq dùng $, Tiền Việt có dấu phẩy
                if t in ["GC=F", "BZ=F", "^IXIC"]:
                    price_str = f"${close_today:,.1f}"
                elif close_today > 1000: 
                    price_str = f"{close_today:,.0f}"
                elif close_today > 10: 
                    price_str = f"{close_today:,.2f}"
                else: 
                    price_str = f"{close_today:,.2f}"

                market_data[t] = {
                    "name": meta[t],
                    "price": price_str,
                    "change": change_pct
                }
            else:
                market_data[t] = {"name": meta[t], "price": "N/A", "change": 0.0}
        except:
            market_data[t] = {"name": meta[t], "price": "N/A", "change": 0.0}

    return market_data, groups
